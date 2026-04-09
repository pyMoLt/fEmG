# fEmG - Elektromyographie-Analyse mit BITalino

Dieses Projekt dient der Erfassung, Analyse und Nutzung von Elektromyographie (EMG) Signalen des Musculus biceps brachii mittels der BITalino Hardware. Das rohe EMG-Signal wird eingelesen, gefiltert und in ein interaktives Biofeedback-System ("EMG Flappy Bird") überführt.

---

## Zuordnung der Teilaufgaben
Das Projekt ist modular aufgebaut, um den Anforderungen der uni-spezifischen Abschlussaufgabe gerecht zu werden. Die Aufgaben sind wie folgt in den Skripten implementiert:


 **Basisfunktionalität Verbidung zum Bitalino (AT-01):** 
  * `src/utils/hardware.py`: Verbidung und Sampling funktioniert
  
    
 **Level Bronze/Silber (AT-02, AT-03, AT-06):** 
  * `src/utils/signal_proc.py` -> `adc_zu_mv()`: Umrechnung der ADC-Rohdaten in Millivolt.
  * `src/bio_feedback.py` -> `plot_emg()`: 10-sekündige Aufnahme und dreistufiger Vergleichs-Plot (ADC -> mV -> Gefiltert)
  * `src/utils/signal_proc.py` -> `hochpassfilter_fft()`: FFT-basierter 30 Hz Hochpassfilter (Entfernung von Bewegungsartefakten).

   
 **Level Gold (AT-04, AT-05):**
  * `src/utils/signal_proc.py` -> `rms()`: Quadratische Gewichtung zur Bestimmung der Signalleistung.
  * `src/bio_feedback.py` -> `mean_activity()` & `is_active()`: Berechnung der Aktivität über ein 0.1s Fenster.
  * `src/gui/emg_tracker.py`: Echtzeit-Visualisierung der Muskelaktivität und absolutem Höchstwert-Tracking.

   
**Level Platin:**
  * `src/gui/flappy_emg.py`: Das "EMG Flappy Bird" Spiel, gesteuert durch Muskelanspannung.
  * AT-Tests und Unit-Test sind integriert. 

    

---

## Projektstruktur
Das Repository ist wie folgt gegliedert:

- `src/`: Der Quellcode des Projekts.
  - `src/utils/hardware.py`: Zentrale Steuerung der BITalino-Kommunikation.
  - `src/utils/signal_proc.py`: Reine Signalverarbeitungs-Logik (Mathematik/Filter).
  - `src/bio_feedback.py`: Controller-Klasse, die Hardware und Signalverarbeitung verbindet.
  - `src/gui/`: Die ausführenden Programme (`emg_tracker.py`, `flappy_emg.py`).
- `tests/`: 
  - `tests/unit/`: Unabhängige Mathematik-Tests (`pytest`).
  - `tests/acceptance/`: Manuelle und halbautomatische Funktions-Tests (AT-01 bis AT-06).
- `docs/`: Referenzen, Architekturplanung und Theorie.
- `assets/`: Referenzvideos und Bilder.
- `archive/`: Referenz-Skripte

---

## Anleitung zum Start (Benutzung)

Um das Projekt lokal auszuführen, müssen folgende Schritte eingehalten werden:

1. **Bluetooth-Parameter setzen:** 
   Öffne die Datei `src/utils/hardware.py` und ändere die Variable `DEFAULT_ADDRESS` auf den Pfad oder die MAC-Adresse deines eigenen BITalino-Sensors.
   * *Mac:* z.B. `"/dev/tty.BITalino-4C-C9"`
   * *Windows/Linux:* z.B. `"20:18:06:13:02:15"`

2. **Schwellenwert kalibrieren:**
   Starte zuerst den Tracker, um zu testen, ab wie viel Millivolt (mV) dein Bizeps als "angespannt" gelten soll.
   ```bash
   python src/gui/emg_tracker.py
   ```
   Trage deinen ermittelten Wert als `SCHWELLENWERT` in `src/gui/flappy_emg.py` ein.

3. **Spiel starten:**
   ```bash
   python src/gui/flappy_emg.py
   ```

---

## Installation

**Wichtiger Hinweis für macOS:** Die offizielle `bitalino`-Bibliothek installiert fehlerhafte Bluetooth-Abhängigkeiten (`pybluez`), die auf Macs zum Absturz führen. Die Installation muss über `no-deps` erfolgen:

```bash
# 1. Virtuelle Umgebung erstellen (Python 3.11 empfohlen)
python3.11 -m venv .venv
source .venv/bin/activate

# 2. bitalino ohne fehlerhafte Abhängigkeiten installieren
pip install bitalino==1.2.6 --no-deps

# 3. Restliche Pakete installieren
pip install -r requirements.txt
```
**Bitalino:** Die Einrichtung des Bitalinos soll der folgenden Webseite (https://support.pluxbiosignals.com/wp-content/uploads/2021/11/bitalino-revolution-user-manual.pdf) entnommen werden. Weiterhin Zur Elektrodenposition und EMG-Berechnung bitte das Datenblatt-EMG (https://support.pluxbiosignals.com/wp-content/uploads/2021/11/electromyography-emg-user-manual.pdf) zu Rate ziehen.

**Python:** Link zu offiziellen Python Bitalino-Bibliothek. https://github.com/bitalinoworld/revolution-python-api



---

## CAVE: Bekannte Einschränkungen (Hardware/OS)
**macOS Bluetooth-Stabilität:** 
Die Verbindung über Bluetooth SPP (Serial Port Profile Classic) hat sich unter macOS als extrem instabil erwiesen. Die offizielle BITalino-Library blockiert den Haupt-Thread auf unbestimmte Zeit, wenn das Gerät nicht sofort antwortet. 

Ob dieses Verhalten unter Windows oder Linux identisch auftritt, konnte nicht abschließend evaluiert werden. Wenn das Skript einfriert oder keine Verbindung aufbaut, ist oft ein **kompletter Reset des Bluetooth-Moduls am Mac** (Deaktivieren/Aktivieren), **Neukoppeln** oder/und ein **Neustart des BITalino** erforderlich.

---

## Architekturentscheidungen
Worauf bei der Implementierung geachtet wurde:

* **Robustheit durch Threading:** Wegen der beschriebenen macOS-Instabilitäten wurden alle kritischen Bluetooth-Aufrufe (`connect`, `read`) in separate Daemons (Threads) mit Timeouts ausgelagert. Dies war eine KI-gestützte Architektur-Empfehlung, um zu verhindern, dass die Hardware-Verbindung einfriert/instabil wird.
* **Saubere Module:** Keine Logik-Dopplung. Die GUI weiß nichts vom BITalino, die Hardware weiß nichts von der FFT. Die Klasse `BioFeedback` agiert als klassischer Controller.
* **Vorlesungsbezug:** Konzepte wie der RMS (Root Mean Square) als Maß für physiologische Kraft oder die Definition der Fenstergrößen der Filter orientieren sich streng an den Vorlesungsinhalten und allgemeinen Bitalino-Referenzen. 
