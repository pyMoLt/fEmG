import matplotlib.pyplot as plt
import sys
import os

# Pfad anpassen, damit Python das src Paket findet
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.bio_feedback import BioFeedback

# ---KONFIGURATION---
# Schwellenwert: Ab diesem RMS-Wert in mV gilt der Muskel als aktiv.
# Vorher bitte mit dem EMG-Tracker ausprobieren und an die eigene Muskelkraft anpassen.
SCHWELLENWERT = 0.05

def main():
    # BioFeedback-Objekt erstellen mit BT-Adresse aus hardware.py
    bf = BioFeedback(threshold=SCHWELLENWERT)

    # Verbindung zum BITalino herstellen und bei Fehler abbrechen
    if not bf.connect():
        print("Konnte keine Verbindung zum [BITalino] herstellen. Beende...")
        return

    # Plot vorbereiten
    plt.ion()  # Plot aktualisiert sich live in der Schleife
    fig, ax = plt.subplots(figsize=(6, 8))

    # Einzelner Balken für die aktuelle Muskelaktivität (RMS-Wert in mV)
    bar_plot = ax.bar(["Muskelaktivität"], [0], color="skyblue")

    ax.set_ylim(0, 0.5)  # Wertebereich wird dynamisch angepasst
    ax.set_ylabel("Aktivität (RMS in mV)")
    ax.set_title("Echtzeit EMG-Tracker")

    # Rote gestrichelte Linie für den Schwellenwert.
    # Als Variable gespeichert, damit sie später per set_ydata() angepasst werden kann.
    threshold_line = ax.axhline(y=SCHWELLENWERT, color='r', linestyle='--', label="Schwellenwert")

    # Grüne Linie für das gleitende Maximum. Steigt sofort bei neuen Höchstwerten
    max_line = ax.axhline(y=0, color='g', linestyle='-', label="Gleit. Maximum")
    ax.legend()

    # Text für den absoluten Höchstwert und zeigt den besten je gemessenen Wert.
    max_label = ax.text(
        0.98, 0.97,
        "Höchstwert: 0.000 mV",
        transform=ax.transAxes,
        ha='right', va='top',
        fontsize=9, color='darkgreen'
    )

    print("Starte Echtzeit-Anzeige. Drücke Strg+C zum Beenden.")

    try:
        max_activity = 0.0   # absoluter Höchstwert der ganzen Session

        while True:
            # Aktuellen RMS-Wert für das letzte 0.1s-Fenster holen
            current_activity = bf.mean_activity()

            # Balkenhöhe aktualisieren
            bar_plot[0].set_height(current_activity)

            # Balken orange wenn Schwellenwert überschritten = Muskel angespannt
            if current_activity > SCHWELLENWERT:
                bar_plot[0].set_color("orange")
            else:
                bar_plot[0].set_color("skyblue")

            # Absoluten Höchstwert der Session im Text aktualisieren
            if current_activity > max_activity:
                max_activity = current_activity
                max_label.set_text(f"Höchstwert: {max_activity:.3f} mV")
                
            # Grüne Linie an den absoluten Höchstwert koppeln
            max_line.set_ydata([max_activity])

            # Dynamische Skalierung der Y-Achse auf den nächsthöheren 0.5-Schritt
            current_ymax = ax.get_ylim()[1]
            
            # Manuelle Berechnung der 0.5 Schritte
            steps = int(max_activity / 0.5)
            if max_activity > steps * 0.5:
                steps += 1
                
            needed_ymax = max(0.5, steps * 0.5)
            
            if needed_ymax > current_ymax:
                ax.set_ylim(0, needed_ymax)

            # Kurze Pause damit matplotlib das Fenster neu zeichnen kann
            plt.pause(0.01)

    except KeyboardInterrupt:
        print("Anzeige durch Nutzer gestoppt.")
    finally:
        bf.disconnect()
        plt.close()


if __name__ == "__main__":
    main()
