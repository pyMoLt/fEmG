# Kernarchitektur (fEmG)

Das System folgt einer sauberen, modularen Architektur, um die Komplexität der Hardware von der Signalverarbeitung und der Benutzeroberfläche zu trennen.

## Die vier Schichten

### 1. Hardware Layer (`src/utils/hardware.py`)
Kapselt die Verbindung zum BITalino. 
- **Besonderheit:** Da die macOS-Bluetooth-Verbindung oft einfriert, laufen die Verbindungsaufbaue und das kontinuierliche Einlesen der Sensordaten sicher in separaten **Hintergrund-Threads**.
- Stellt einen "Stream-Modus" (für das Spiel) und einen "Episoden-Modus" (für Plots) zur Verfügung.

### 2. Processing Layer (`src/utils/signal_proc.py`)
Die reine Mathematik der Signalverarbeitung ist komplett unabhängig von der Hardware, was das Testen vereinfacht.
- **Normalisierung**: Umrechnung der Integer-Rohdaten in Millivolt (mV) nach BITalino-Datenblatt.
- **Filterung**: Ein FFT-basierter 30Hz Hochpassfilter blockiert Rauschen und langsame Bewegungsartefakte.
- **RMS**: Berechnung der Kontraktionsstärke über den quadratischen Mittelwert (RMS).

### 3. Application Layer (`src/bio_feedback.py`)
Die Klasse `BioFeedback` ist der Controller. Sie orchestriert Hardware und Funktionen.
- Liefert die in der Aufgabe geforderten Checkpoint-Schnittstellen: `plot_emg()`, `mean_activity()`, `is_active()`.
- Speichert die Bluetooth-Stabilität und verwaltet das saubere Trennen beim Beenden.

### 4. Presentation Layer (`src/gui/`)
Grafische Übersicht zur Präsentation. Die GUI nutzt ausschließlich Funktionen aus `src/bio_feedback.py`.
- **`emg_tracker.py`**: Echtzeit-Visualisierung der Muskelaktivität. Nutzt Matplotlib, hat eine dynamische Max-Linie und merkt sich den stärksten Rekord (Absoluter Maximalwert).
- **`flappy_emg.py`**: Das fertige Biofeedback-Spiel (Flappy Bird). Steigt, wenn `is_active()` True meldet.
