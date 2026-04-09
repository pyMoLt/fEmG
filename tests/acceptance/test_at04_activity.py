# AT-04: Maximale Muskelaktivität (mean_activity)
#
# Dieser Test überprüft, ob die maximale Muskelaktivität entsprechend dem emg_tracker.py richtig abgegriffen wird, 
# der Balken auf Anspannung reagiert und das Maximum angepasst wird.
#
# Starten: python tests/acceptance/test_at04_activity.py

import sys
import os


def main():
    print("AT-04: Maximale Muskelaktivität (mean_activity)")
    print("Dies ist ein manueller Test mit der Hardware.\n")

    print("Schritte:")
    print("1. Starte den EMG-Tracker: python src/gui/emg_tracker.py")
    print("2. Lasse den Bizeps für 3 Sekunden locker (Ruhezustand).")
    print("3. Spanne den Bizeps für 3 Sekunden stark an.")

    print("\nErwartetes Ergebnis:")
    print("- Der Balken bleibt im Ruhezustand nahe 0 mV.")
    print("- Bei Anspannung steigt der Balken deutlich an.")
    print("- Die grüne Linie (gleitendes Maximum) folgt dem Balken nach oben.")
    print("- Der Höchstwert oben rechts zeigt den besten gemessenen Wert.")

    print("Frage: Hat der Balken auf deine Anspannung reagiert? (j/n)")
    answer = input("Antwort: ")

    if answer.lower() == 'j':
        print("ERGEBNIS: AT-04 BESTANDEN (manuell bestätigt)!")
    else:
        print("ERGEBNIS: AT-04 NICHT BESTANDEN.")


if __name__ == "__main__":
    main()
