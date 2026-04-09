import pygame
import random
import sys
import os

# Pfad anpassen, damit wir src finden
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.bio_feedback import BioFeedback

# --- KONFIGURATION ---
# Schwellenwert: Ab diesem RMS-Wert gilt der Muskel als aktiv, heißt der Vogel fliegt.
# Vorher mit dem emg_tracker.py bestimmen, welcher Wert zur eigenen Muskelkraft passt.
SCHWELLENWERT = 0.08

# Start pygame
pygame.init()

# Fenstergröße und Farben
SCREEN_WIDTH  = 500
SCREEN_HEIGHT = 600

# Farben als RGB-Tupel
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED   = (200, 0, 0)

# Vogelgröße und Frabe
BIRD_WIDTH  = 30
BIRD_HEIGHT = 30
BIRD_COLOR  = RED

# Rohr-Parameter: Breite, Farbe, Geschwindigkeit (Pixel/Frame), Lücke zwischen Rohren
PIPE_WIDTH = 50
PIPE_COLOR = GREEN
PIPE_SPEED = 3
PIPE_GAP   = 200 

# Initiliasieren des screens
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("EMG Flappy Bird. Spanne den Muskel an!")

# Clock für Fps Kontrolle
clock = pygame.time.Clock()

# Vogel-Klasse: Beinhaltet Position, Physik und die EMG-Steuerung.
# Der Vogel steigt, wenn der Muskel aktiv ist (BF.is_active() = True), sonst zieht Schwerkraft ihn nach unten.
class Bird:
    def __init__(self):
        self.reset()

    def reset(self):
        # Startposition in der Mitte des Bildschirms (eigene Erweiterung für Neustart)
        self.x        = 100
        self.y        = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.gravity  = 0.5   # Beschleunigung nach unten pro Frame
        self.lift     = -10   # Impuls nach oben bei Muskelanspannung ggf. Anpassen für Spielbarkeit

    def update(self):
        # Muskelaktivität abfragen. 
        # is_active() nutzt mean_activity() + Schwellenwert
        if BF.is_active():
            self.velocity = self.lift  # Sofortiger Aufwärtsimpuls
        else:
            self.velocity += self.gravity  # Schwerkraft
        self.y += self.velocity

    def draw(self):
        pygame.draw.rect(screen, BIRD_COLOR, (self.x, self.y, BIRD_WIDTH, BIRD_HEIGHT))

# Rohr-Klasse mit zufallsbasierter Lücke, bewegt sich von rechts nach links.
class Pipe:
    def __init__(self, x):
        self.x = x
        # Zufällige Höhe des oberen Rohrs, Lücke hat immer PIPE_GAP px Platz
        self.top_height    = random.randint(50, SCREEN_HEIGHT - PIPE_GAP - 50)
        self.bottom_height = SCREEN_HEIGHT - self.top_height - PIPE_GAP

    def update(self):
        self.x -= PIPE_SPEED  # Rohr bewegt sich nach links

    def draw(self):
        # Oberes Rohr (von oben))
        pygame.draw.rect(screen, PIPE_COLOR, (self.x, 0, PIPE_WIDTH, self.top_height))
        # Unteres Rohr (vom Boden)
        pygame.draw.rect(
            screen, PIPE_COLOR, (self.x, SCREEN_HEIGHT - self.bottom_height, PIPE_WIDTH, self.bottom_height)
        )

    def is_off_screen(self):
        return self.x + PIPE_WIDTH < 0

    def collides_with(self, bird):
        # Kollision: Vogel berührt oberes oder unteres Rohr horizontal
        if (
            bird.y < self.top_height
            or bird.y + BIRD_HEIGHT > SCREEN_HEIGHT - self.bottom_height
        ) and self.x < bird.x + BIRD_WIDTH and self.x + PIPE_WIDTH > bird.x:
            return True
        return False

# Startbildschirm anzeigen (eigene Erweiterung, im Original nicht vorhanden).
# Zeigt letzen Score, wenn vorhanden, wartet auf Space-taste zum Starten.
def show_start_screen(last_score=None):
    screen.fill(WHITE)
    font_large = pygame.font.SysFont(None, 48)
    font_small = pygame.font.SysFont(None, 24)

    title     = font_large.render("EMG Flappy Bird", True, BLACK)
    instr     = font_small.render("Spanne den Muskel an, um zu springen!", True, BLACK)
    start_msg = font_large.render("Drücke SPACE zum Starten", True, GREEN)

    screen.blit(title,     (SCREEN_WIDTH // 2 - title.get_width()     // 2, 150))
    screen.blit(instr,     (SCREEN_WIDTH // 2 - instr.get_width()     // 2, 220))
    screen.blit(start_msg, (SCREEN_WIDTH // 2 - start_msg.get_width() // 2, 400))

    if last_score is not None:
        score_msg = font_large.render(f"Letzter Score: {last_score}", True, RED)
        screen.blit(score_msg, (SCREEN_WIDTH // 2 - score_msg.get_width() // 2, 300))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                BF.disconnect()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    waiting = False

# Main game loop
def main():
    # BF als global deklarieren, damit Bird.update() und show_start_screen() drauf zugreifen.
    # BioFeedback-Objekt erst hier erstellen und nicht auf Modulebene, damit kein Bluetooth-Verbindungsversuch beim bloßen Importieren der Datei stattfindet.
    global BF
    BF = BioFeedback(threshold=SCHWELLENWERT)
    if not BF.connect():
        print("Konnte keine Verbindung zum [BITalino] herstellen. Beende...")
        pygame.quit()
        sys.exit()

    # Eigene Erweiterung: Mehrere Runden möglich (statt einmaligem Spielende wie im Original)
    last_score = None
    
    try:
        while True:
            # Startbildschirm anzeigen
            show_start_screen(last_score)
            
            # Spiel-Variablen initialisieren
            bird = Bird()
            pipes = [Pipe(SCREEN_WIDTH + i * 250) for i in range(3)]
            score = 0
            game_running = True
            
            # Font einmal pro Runde erstellen
            font = pygame.font.SysFont(None, 36)
            
            # Die eigentliche Spiel-Runde
            while game_running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        BF.disconnect()
                        sys.exit()

                # Update bird
                bird.update()

                # Update pipes
                for pipe in pipes:
                    pipe.update()
                    if pipe.is_off_screen():
                        pipes.remove(pipe)
                        pipes.append(Pipe(SCREEN_WIDTH + 50))
                        score += 1

                    if pipe.collides_with(bird):
                        game_running = False #  Nur die Runde beenden, nicht das Programm

                # Check, ob bird den Boden oder Himmel berührt
                if bird.y < 0 or bird.y + BIRD_HEIGHT > SCREEN_HEIGHT:
                    game_running = False # Zurück zum Startbildschirm bei Fehler

                # Darstellung
                screen.fill(WHITE)
                bird.draw()
                for pipe in pipes:
                    pipe.draw()

                # Score anzeigen
                score_text = font.render(f"Score: {score}", True, BLACK)
                screen.blit(score_text, (10, 10))

                pygame.display.flip()
                clock.tick(60) 
            
            # Score speichern für den nächsten Startbildschirm
            last_score = score
            # Kurze Pause
            pygame.time.wait(500)
            
    finally:
        # Verbindung immer trennen bei Programmende
        BF.disconnect()
        pygame.quit()

if __name__ == "__main__":
    main()
