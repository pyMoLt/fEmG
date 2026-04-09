import pygame
import random
import sys
import project as p

# TODO: Parameter für Konstruktor von BioFeedback eintragen
BF = p.BioFeedback()

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

# Bird settings
BIRD_WIDTH = 30
BIRD_HEIGHT = 30
BIRD_COLOR = RED

# Pipe settings
PIPE_WIDTH = 50
PIPE_COLOR = GREEN
PIPE_SPEED = 7
PIPE_GAP = 350



# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("One-Button Flappy Bird")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Bird class
class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.gravity = 0.5
        self.lift = -10

    def update(self):
        if BF.is_active():
            self.velocity = self.lift
        else:
            self.velocity += self.gravity
        self.y += self.velocity

    def draw(self):
        pygame.draw.rect(screen, BIRD_COLOR, (self.x, self.y, BIRD_WIDTH, BIRD_HEIGHT))

# Pipe class
class Pipe:
    def __init__(self, x):
        self.x = x
        self.top_height = random.randint(50, SCREEN_HEIGHT - PIPE_GAP - 40)
        self.bottom_height = SCREEN_HEIGHT - self.top_height - PIPE_GAP

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self):
        # Draw top pipe
        pygame.draw.rect(screen, PIPE_COLOR, (self.x, 0, PIPE_WIDTH, self.top_height))
        # Draw bottom pipe
        pygame.draw.rect(
            screen, PIPE_COLOR, (self.x, SCREEN_HEIGHT - self.bottom_height, PIPE_WIDTH, self.bottom_height)
        )

    def is_off_screen(self):
        return self.x + PIPE_WIDTH < 0

    def collides_with(self, bird):
        if (
            bird.y < self.top_height
            or bird.y + BIRD_HEIGHT > SCREEN_HEIGHT - self.bottom_height
        ) and self.x < bird.x + BIRD_WIDTH and self.x + PIPE_WIDTH > bird.x:
            return True
        return False

# Main game loop
def main():
    bird = Bird()
    pipes = [Pipe(SCREEN_WIDTH + i * 200) for i in range(3)]
    score = 0

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update bird
        bird.update()

        # Update pipes
        for pipe in pipes:
            pipe.update()
            if pipe.is_off_screen():
                pipes.remove(pipe)
                pipes.append(Pipe(SCREEN_WIDTH))
                score += 1

            if pipe.collides_with(bird):
                running = False

        # Check if bird hits the ground or flies too high
        if bird.y < 0 or bird.y + BIRD_HEIGHT > SCREEN_HEIGHT:
            running = False

        # Draw everything
        screen.fill(WHITE)
        bird.draw()
        for pipe in pipes:
            pipe.draw()

        # Display score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(180)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
