# AT-05: Trigger-Logik (is_active)
#
# Dieser Test prüft ob is_active() zuverlässig True/False zurückgibt
# und damit das Spiel steuerbar ist. Kann nicht automatisiert werden.
#
# Starten: python tests/acceptance/test_at05_trigger.py

import sys
import os


def main():
    print("AT-05: Trigger-Logik (is_active)")
    print("Dies ist ein manueller Test mit der Hardware.\n")

    print("Schritte:")
    print("1. Starte das Spiel: python3 src/gui/flappy_emg.py")
    print("2. Spanne den Muskel an. Der Vogel sollte steigen.")
    print("3. Entspanne den Muskel. Der Vogel sollte fallen.")

    print("Erwartetes Ergebnis:")
    print("Der Vogel reagiert fast zeitgleich zur Anspannung (Latenz < 100ms).")
    print("Im Ruhezustand (kein Muskel angespannt) fällt der Vogel zuverlässig.")
    print("Leichtes Hintergrundrauschen löst keinen false-positive Sprung aus.")

    print("Frage: Konntest du den Vogel mit deinem Muskel steuern? (j/n)")
    answer = input("Antwort: ")

    if answer.lower() == 'j':
        print("ERGEBNIS: AT-05 BESTANDEN (manuell bestätigt)!")
    else:
        print("ERGEBNIS: AT-05 NICHT BESTANDEN.")


if __name__ == "__main__":
    main()
