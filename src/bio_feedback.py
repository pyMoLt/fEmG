import time
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Pfad anpassen, damit Python das src Paket findet und Importieren der selbstgeschriebenen Module.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.utils.hardware import BitalinoConnector
from src.utils.signal_proc import adc_to_mv, hochpassfilter_fft, mean_activity


# BioFeedback ist die Hauptklasse des Projekts und verbindet Hardware und Signalverarbeitung.
# Sie dient als eine Art Koordiantor, wobei die GUI-Skripte (emg_tracker, flappy_emg)
# nur diese Klasse aufrufen und sich nicht um die BITalino-Kommunikation oder Signalverarbeitung kümmern müssen.
class BioFeedback:

    def __init__(self, mac_address=None, threshold=0.1):
        # mac_adresse: Bluetooth-Adresse des BITalino (None = Standardwert aus hardware.py)
        # threshold: RMS-Wert in mV, ab dem is_active() True zurückgibt.
        # Dieser lässt sich empirisch bestimmen, indem man:
        # - Ruhewert misst (Arm entspannt für ca. 3s), dann notieren
        # - Maximalwert misst (Arm angespannt für ca. 3s), dann notieren
        # -> Schwellenwert = Ruhewert + (Maximalwert-Ruhewert)*0.3
        # Nutze emg_tracker.py, um geeignete Werte abzulesen/Einzutragen in GUI-Scripten
        
        self.mac_address = mac_address
        self._threshold = threshold
        self.is_connected  = False  # Frühzeitig stellen, damit __del__ funktioniert

        # Hardware-Objekt erstellen (kümmert sich um Bluetooth, Streaming, Puffer) aus Hardware.py
        self.device = BitalinoConnector(address=self.mac_address)

    # Stellt die Bluetooth-Verbindung zum BITalino her.
    # Gibt True zurück wenn erfolgreich, sonst False.
    def connect(self):
        print(f"Versuche Verbindung zu {self.device.address} herzustellen...")
        if self.device.connect():
            self.is_connected = True
            print("Verbindung erfolgreich!")
            return True
        else:
            print("Verbindung fehlgeschlagen!")
            return False

    # Trennt die Verbindung sauber (stoppt Stream, schließt Bluetooth-Port).
    # hasattr verhindert Fehler, wenn das Objekt vor Abschluss des __init__ gelöscht wird.
    def disconnect(self):
        if hasattr(self, 'is_connected') and self.is_connected:
            self.device.close()
            self.is_connected = False
            print("Verbindung getrennt.")

    # Aufgabe b): Sammelt 10 Sekunden EMG-Daten und plottet den Verarbeitungsweg.
    # Zeigt drei Plots übereinander: Rohdaten (ADC) zu mV zu gefiltertes Signal.
    # So lässt sich der Effekt der Umrechnung und des Filters besser vergleichen.
    def plot_emg(self):
        if not self.is_connected:
            print("Bitte zuerst verbinden!")
            return

        # Aufnahme starten (1000 Hz, Kanal A1 = Index 0 im BITalino-Array)
        # Ohne start() liefert read_episode() kein Ergebnis
        if not self.device.start(rate=1000, channels=[0]):
            print("Aufnahme konnte nicht gestartet werden.")
            return

        print("Sammle 10 Sekunden EMG-Daten...")
        # 10 Sekunden × 1000 Hz = 10.000 Samples (Integer, kein Float)
        data_raw = self.device.read_episode(10_000)

        # Aufnahme stoppen: So kann danach der Stream für mean_activity() neu starten
        self.device.stop()

        if data_raw is None or len(data_raw) == 0:
            print("Keine Daten empfangen.")
            return

        # Auswahl aller Zeilen und Auswahl Spalte 5 des BITalino-Arrays (Kanal A1 = EMG-Signal)
        # Output: 1-dim Array mit Roh-Daten (ADC) (0-1023) über die zeit
        emg_raw = data_raw[:, 5] 

        # Schritt 1: ADC-Integer zu Millivolt (Aufgabe b, Bronze)
        emg_mv = adc_to_mv(emg_raw)

        # Schritt 2: 30 Hz Hochpassfilter anwenden (Aufgabe b, Silber)
        emg_filtered = hochpassfilter_fft(emg_mv, cutoff_hz=30)

        # Schritt 3: Visualisierung mit Zeitachse in Sekunden (bei 1000 Hz = Index / 1000)
        t = np.arange(len(emg_raw)) / 1000.0

        # Drei Subplots: zeigen den kompletten Verarbeitungsweg, sharex für gemeinsame x-achse
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

        # Oberster Plot: Rohdaten direkt vom Sensor (ADC-Integer, 0–1023)
        ax1.plot(t, emg_raw, color='gray', linewidth=0.5)
        ax1.set_title("Rohdaten (ADC-Werte, 0–1023)")
        ax1.set_ylabel("ADC-Wert")

        # Mittlerer Plot: Nach der mV-Umrechnung (nullzentriert um ca.0 mV)
        ax2.plot(t, emg_mv, color='blue', linewidth=0.5)
        ax2.set_title("EMG Signal (in mV, ungefilter)")
        ax2.set_ylabel("Spannung [mV]")

        # Unterer Plot: Nach dem 30 Hz Hochpassfilter (Gleichanteil und Artefakte entfernt)
        ax3.plot(t, emg_filtered, color='green', linewidth=0.5)
        ax3.set_title("Gefiltertes EMG Signal (30 Hz Hochpass)")
        ax3.set_ylabel("Spannung [mV]")
        ax3.set_xlabel("Zeit [s]")

        plt.tight_layout()
        plt.show()

    # Aufgabe c): Berechnet die aktuelle Muskelaktivität als einzelnen RMS-Wert.
    # Liest die neuesten 100 Samples (= 0.1s bei 1000 Hz) aus dem Hintergrund-Stream,
    # rechnet sie in mV um, filtert sie und berechnet dann den RMS-Wert.
    # Gibt 0.0 zurück wenn keine ausreichenden Daten vorliegen.
    def mean_activity(self):
        if not self.is_connected:
            return 0.0

        # Stream automatisch starten wenn er noch nicht läuft.
        # Der Stream liest kontinuierlich Daten in einen Puffer (hardware.py),
        # damit mean_activity() jederzeit die letzten Samples abrufen kann.
        if not self.device._streaming:
            self.device.start_stream()
            # Kurze Pause: Bluetooth SPP braucht einen Moment zum Stabilisieren,
            # sonst ist der Puffer beim ersten Aufruf noch leer oder fehlerhaft.
            time.sleep(0.2)

        # Neueste 100 Samples aus dem Puffer holen, check ob tatsächlich 100 DAtenpunkte vorliegen
        data = self.device.read_latest(100)
        if data is None or len(data) < 100:
            return 0.0

        # Verarbeitungskette: Spalte 5 (A1) zu mV zu gefiltert zu RMS
        emg_raw      = data[:, 5]
        emg_mv       = adc_to_mv(emg_raw)
        emg_filtered = hochpassfilter_fft(emg_mv, cutoff_hz=30)

        # mean_activity() aus signal_proc berechnet RMS über das 0.1s-Fenster
        activity = mean_activity(emg_filtered)
        return activity

    # Aufgabe d): Gibt True zurück wenn der Muskel angespannt ist, sonst False.
    # Vergleicht den aktuellen RMS-Wert direkt mit dem eingestellten Schwellenwert.
    def is_active(self):
        return self.mean_activity() > self._threshold

    # Hilfsfunktion zur Kalibrierung: Schwellenwert manuell anpassen.
    # Empirische Bestimmung: Ruhewert + 30% der Differenz (Ruhewert, Maximalwert) als Startwert.
    # Sinnvoll wenn der Standardwert für eine Person zu hoch oder zu niedrig ist.
    # Aufruf z.B.: bf.set_threshold(0.08).
    # Aktuell ungenuztzt! 
    def set_threshold(self, value):
        self._threshold = value
        print(f"Neuer Schwellenwert: {value}")

    # Stellt sicher, dass die Verbindung beim Beenden getrennt wird.
    # hasattr verhindert Fehler, falls __init__ nicht vollständig lief.
    def __del__(self):
        try:
            if hasattr(self, 'is_connected') and self.is_connected:
                self.disconnect()
        except:
            pass