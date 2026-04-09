# Detaillierte Acceptance Tests (AT-Tests)

Diese Tests dienen als Überprüfung der Kernanforderungen des Projekts. Einige Tests laufen vollautomatisch als Skript, andere erfordern manuelle Hardwarebedienung. Alle Tests können einzeln gestartet werden.



## AT-01: Connection Test (Konnektivität)
- **Beschreibung**: Prüft, ob sich das System mit dem BITalino verbinden und Daten auslesen kann.
- **Skript**: `python tests/acceptance/test_at01_connection.py`
- **Ablauf**: 
  1. Skript fragt, ob ein einzelner Block (Episode) oder ein Stream gelesen werden soll.
  2. Es verbindet sich, liest Daten, und trennt sich wieder sauber.
- **Ziel**: Eine Zeile mit Array-Daten erscheint auf der Konsole, kein freezed Thread!

## AT-02: Signal-Transformation (ADC zu mV)
- **Beschreibung**: Prüft die mathematische Umrechnung von Roh-Integer (0-1023) in echte Spannungswerte.
- **Skript**: `python tests/acceptance/test_at02_transformation.py`
- **Ablauf**: Speist die Werte 0, 512, 1023 in die Formel ein.
- **Ziel**: Das Skript meldet "BESTANDEN", da 512 nahe 0 mV liegt und die Extreme bei ca. ±1.6 mV liegen.

## AT-03: Hochpass-Filterung (30Hz)
- **Beschreibung**: Prüft die Fourier-Transformation (FFT Filter).
- **Skript**: `python tests/acceptance/test_at03_filtering.py`
- **Ablauf**: Erzeugt ein synthetisches Rauschen (10Hz) vermischt mit einem echten Signal (100Hz). Der Filter muss das 10Hz-Rauschen wegschneiden.
- **Ziel**: Das Skript meldet "BESTANDEN": Die 100Hz Welle bleibt erhalten, die 10Hz ist eliminiert.

## AT-04: Maximale Muskelaktivität (Aktion/Ruhe)
- **Beschreibung**: Manuelle Prüfung der `mean_activity()` Funktion und der Visualisierung.
- **Skript**: `python tests/acceptance/test_at04_activity.py`
- **Ablauf**: 
  1. Skript leitet durch die Tests.
  2. Arm entspannen: Balken muss sinken.
  3. Bizeps anspannen: Balken muss stark ausschlagen.
- **Ziel**: Grüne Linie wandert dynamisch mit dem Ausschlag der Muskelaktivität, der Tracker merkt sich oben rechts den besten Rekord. Skript fragt danach "Bestanden? (j/n)".

## AT-05: Trigger-Logik (Flappy Bird)
- **Beschreibung**: Manuelle Prüfung von `is_active()` im echten Szenario.
- **Skript**: `python tests/acceptance/test_at05_trigger.py`
- **Ablauf**: Spiel starten, Muskel schnell anspannen und entspannen.
- **Ziel**: Der Vogel fliegt hoch bei Anspannung und fällt bei Entspannung, ohne spürbare Verzögerung. Leichtes Wackeln im Ruhezustand (Rauschen) darf keinen "false-positive" Sprung auslösen. Skript fragt danach "Bestanden? (j/n)".

## AT-06: 10-Sekunden Visualisierung (plot_emg)
- **Beschreibung**: Systematische Prüfung der Aufgabe B. Überprüft, ob Signale erfasst, gewandelt, gefiltert und visuell im Ganzen dargestellt werden können.
- **Skript**: `python tests/acceptance/test_at06_plot.py`
- **Ablauf**: 
  1. Skript startet und fordert dich auf, den Arm für 10 Sekunden zu bewegen (anspannen/entspannen).
  2. Nach 10 Sekunden poppt ein Fenster von Matplotlib auf.
- **Ziel**: Ein Fenster öffnet sich mit exakt drei Graphen untereinander: ADC (Roh), Millivolt umgerechnet, Gefiltert (ohne Rauschen/DC-Offset). Skript fragt danach "Bestanden? (j/n)".
