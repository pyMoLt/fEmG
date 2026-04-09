# AT-06: 10-Sekunden Visualisierung (plot_emg)
#
# Dieser Test fragt die Anforderung Teilaufgabe B ab.
# Über BioFeedback wird eine 10 Sekunden (10.000 Samples)
# lange Episode aufgezeichnet und anschließend statisch in 3 Plots visualisiert:
# Roh (ADC) -> Umgerechnet (mV) -> Gefiltert (30Hz Hochpass).
#
# Starten: python tests/acceptance/test_at06_plot.py

import sys
import os

# Den Pfad anpassen, damit src gefunden wird
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.bio_feedback import BioFeedback

def main():
    print("AT-06: Signal-Plot (plot_emg)")
    print("Dieser Test zeichnet für 10 Sekunden ein EMG-Signal auf und")
    print("öffnet anschließend einen Plot mit 3 Sub-Graphen.")
    print("Voraussetzung: Das Gerät ist via Bluetooth gekoppelt.")

    input("Drücke ENTER, sobald du bereit bist und das Gerät an ist.")
    print("Verbinde zum Gerät...")

    bf = BioFeedback()
    if not bf.connect():
        print("ERGEBNIS: AT-06 NICHT BESTANDEN (Keine Verbindung).")
        return

    print("Verbindung steht! Bitte den Muskel (Bizeps) für 10 Sekunden abwechselnd anspannen / loslassen.")
    print("Aufzeichnung läuft...")
    
    # plot_emg() liest automatisch 10.000 Samples bei 1000 Hz = 10 Sekunden
    bf.plot_emg()

    # Nachdem das Plot-Fenster geschlossen wurde, fragen wir das Ergebnis ab
    print("Frage: Hat sich ein Fenster geöffnet, in dem die drei Signal-Verarbeitungsstufen")
    print("(Rohdaten ADC -> Millivolt -> Gefiltert) visuell dargestellt wurden? (j/n)")
    answer = input("Antwort: ")

    if answer.lower() == 'j':
        print("ERGEBNIS: AT-06 BESTANDEN (manuell bestätigt)!")
        print("Teilaufgabe B erfolgreich abgeschlossen.")
    else:
        print("ERGEBNIS: AT-06 NICHT BESTANDEN.")

    print("Trenne Verbindung...")
    bf.disconnect()

if __name__ == "__main__":
    main()
