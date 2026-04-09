import numpy as np

# --- Hardwarekonstanten des BITalino EMG-Sensors ---
# Quelle: BITalino Datenblatt
# https://support.pluxbiosignals.com/wp-content/uploads/2021/11/revolution-emg-sensor-datasheet-1.pdf
VCC   = 3.3    # Versorgungsspannung des BITalino in Volt
G_EMG = 1009   # Verstärkungsfaktor (Gain) des verbauten EMG-Sensors


# Rechnet BITalino-Rohdaten (ADC-Integer, 0–1023) in Millivolt um.
# Formel aus dem BITalino-Datenblatt: EMG [mV] = (ADC / 2^10 - 0.5) * VCC / G_EMG * 1000
# Der Nenner ist 2^10 = 1024, weil di ersten vier Channel mit 10bits gesampelt werden 
# Ausgabebereich laut Datenblatt: ca. -1.64 mV bis +1.64 mV
def adc_to_mv(adc_value):
    mv_value = ((adc_value / 1024) - 0.5) * VCC / G_EMG * 1000
    return mv_value


# Hochpassfilter mit Grenzfrequenz 30 Hz, realisiert über die FFT.
# Warum FFT? Die Fouriertransformation wandelt das Signal vom Zeitbereich
# in den Frequenzbereich. Als solches ist es einfach gewisse Anteile des siganls zu filtern/nullen.
# Die inverse FFT (ifft) gibt das gefilterte Signal zurück.
# Warum 30 Hz Grenzfrequenz? EMG-Nutzsignal liegt typisch bei 30–500 Hz.
# Darunter liegen Bewegungsartefakte, Gleichspannungsanteile und der Herzschlag ( um 1 Hz)
def hochpassfilter_fft(signal, cutoff_hz=30, fs=1000):
    n           = len(signal)
    # Signal in den Frequenzbereich transformieren
    y_fft       = np.fft.fft(signal)
    # Frequenzachse berechnen (in Hz, positiv und negativ)
    frequencies = np.fft.fftfreq(n, d=1/fs)
    # Alle Anteile unter 30 Hz nullen (np.abs fängt beide Seiten des Spektrums)
    y_fft[np.abs(frequencies) < cutoff_hz] = 0
    # Zurück in den Zeitbereich, aber nur Realteil
    filtered_signal = np.fft.ifft(y_fft).real
    return filtered_signal


# Berechnet den Root Mean Square (RMS) des Signals.
# Formel: RMS = sqrt(mean(x^2))
#
# Warum RMS statt Mean Absolute Value?
#
# Zum einen wegen der Quadratische Gewichtung: Da RMS jeden Wert vor dem Mitteln quadriert, 
# werden Hohe Amplituden (starke Muskelkontraktionen) dadruch überproportional stärker gewichtet als kleine.
# MAV behandelt alle Amplituden gleich linear. 
#  -> RMS reagiert empfindlicher auf Anspannung, macht den Schwellenwert klarer trennbar.
#
# RMS entspricht der Physiologische Signalleistung: 
# RMS ist dem Effektivwert des Signals gleich, und dabei proportional zur elektrischen Leistung (V^2/R).
# Diese Leistung korreliert mit der aufgewendeten Muskelkraft
#  
# MAVs Vorteil (Robustheit gegen Extremwerte) ist hier weniger relevant:
# Der 30 Hz Hochpassfilter entfernt bereits Bewegungsartefakte. 
# Was danach übrig bleibt sind echte Aktionspotenziale 
#  -> hohe Amplituden sind erwunscht, weil sie starke Kontraktionen signalisieren.
#
# (ausführlichere Diskussion im Methodenteil des Berichts)
# Signal mv als Platzhalter
def rms(signal_mv):
    rms_value = np.sqrt(np.mean(signal_mv ** 2))
    return float(rms_value)


# Berechnet die Muskelaktivität für ein kurzes Zeitfenster (standardmäßig 0.1s).
# Bei 1000 Hz entspricht das den letzten 100 Samples.
# Gibt einen einzelnen RMS-Wert zurück, der zwischen Zeitfenstern vergleichbar ist.
def mean_activity(signal_mv, window_size=100):
    # Nur das neueste 0.1s-Fenster auswerten
    window_data = signal_mv[-window_size:]
    return rms(window_data)
