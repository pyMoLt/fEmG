# AT-01: Verbindungstest (Hardware-Konnektivität)
#
# Testet ob das BITalino gefunden, verbunden und ausgelesen werden kann.
# Bietet zwei Modi an: Episode-Read (einmalig) und kontinuierlicher Stream.
# Voraussetzung: BITalino eingeschaltet und per Bluetooth gekoppelt.
#
# Starten: python tests/acceptance/test_at01_connection.py

import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.utils.hardware import BitalinoConnector

# hier anpassen
# macOS:          "/dev/tty.BITalino-XXXX"
# Windows/Linux:  "XX:XX:XX:XX:XX:XX"
ADDRESS  = "/dev/tty.BITalino-4C-C9" 
RATE     = 1000
CHANNELS = [0]
SAMPLES  = 100


def main():
    device = BitalinoConnector(ADDRESS)

    print("AT-01 Verbindungstest")
    print(f"Adresse: {ADDRESS}")

    try:
        # verbinden
        if not device.connect():
            print("Verbindung fehlgeschlagen, Abbruch.")
            return
        if not device.start(rate=RATE, channels=CHANNELS):
            print("Start fehlgeschlagen, Abbruch.")
            return

        # fragen was gemacht werden soll
        print("Was möchtest du testen?")
        print(" 1. Episode-Read (einmalig n Samples lesen)")
        print(" 2. Stream (kontinuierlich, Enter zum Stoppen)")
        choice = input("Auswahl (1/2): ").strip()

        if choice == "1":
            # so oft lesen wie der User will
            while True:
                answer = input("Enter = lesen, q = beenden").strip().lower()
                if answer == "q":
                    break
                
                print(f"[BITalino] Lese {SAMPLES} Samples.")
                daten = device.read_episode(SAMPLES)
                
                if daten is not None:
                    print(f"[OK] {len(daten)} Samples empfangen.")
                    # Kurzer Auszug für visuelle Kontrolle
                    print("Auszug Channel A1 (Rohwerte):", daten[:5, 5])
                else:
                    print("[FEHLER] Kein Array zurückbekommen.")

        elif choice == "2":
            device.stop() # Episode mode stop, weil start_stream() intern den Start regelt
            device.start_stream(rate=RATE, channels=CHANNELS)
            
            print("Stream läuft im Hintergrund. Drücke ENTER zum Abrufen oder 'q' zum Beenden.")
            while True:
                answer = input("").strip().lower()
                if answer == "q":
                    break
                
                # Wir holen uns einfach was im Puffer ist, maximal 50
                daten = device.read_latest(50)
                if daten is not None and len(daten) > 0:
                    print(f"Gelesen: {len(daten)} Samples. Spalte A1: {daten[-3:, 5]} (letzte 3)")
                else:
                    print("Puffer gerade leer.")
                    
            device.stop_stream()

        else:
            print("Ungültige Auswahl.")

    except KeyboardInterrupt:
        print("Vom Nutzer abgebrochen.")
        
    except Exception as e:
        # Fängt alle anderen unerwarteten Python-Crashes ab
        print(f"\n\n[Fehler] Ein unerwarteter Fehler ist aufgetreten: {e}")
        
    finally:
        # am Ende immer aufräumen
        print("Schließe Verbindung...")
        try:
            # Falls die Verbindung gar nicht erst zustande kam, 
            # könnte close() selbst einen Fehler werfen, daher nochmal try/except.
            device.close()
            print("Port erfolgreich freigegeben.")
        except Exception as e:
            print(f"Konnte nicht sauber schließen: {e}")
        print("Fertig.")


if __name__ == "__main__":
    main()