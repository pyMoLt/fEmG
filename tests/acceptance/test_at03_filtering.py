# AT-03: Hochpass-Filterung (30 Hz)
#
# Prüft ob hochpassfilter_fft() korrekt filtert. Dazu wird ein künstliches
# Testsignal aus 10 Hz (Störung, soll gefiltert werden) und 100 Hz (Nutzsignal,
# soll erhalten bleiben) erzeugt. Nach dem Filter wird per FFT geprüft ob
# die 10 Hz-Amplitude nahezu 0 und die 100 Hz-Amplitude erhalten ist.
#
# Starten: python tests/acceptance/test_at03_filtering.py
import sys
import os
import numpy as np

# Den Pfad anpassen, damit wir src finden
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.utils.signal_proc import hochpassfilter_fft

def main():
    print("AT-03: Hochpass-Filterung (30Hz)")
    
    # Abtastrate und Zeit-Array generieren (1000 Samples = 1 Sekunde)
    fs = 1000
    time = np.arange(0, 1.0, 1/fs)

    # Erzeuge ein EMG-Nutzsignal bei hoher Frequenz, z.B. 100 Hz Kontraktion
    clean_signal = np.sin(2 * np.pi * 100 * time)

    # Erzeuge niederfrequentes Rauschen, z.B. Herzschlag, oder Bewegung
    noise = np.sin(2 * np.pi * 2 * time)

    # Vermische beide Signale (Das ist das Sensorsignal)
    mixed_signal = clean_signal + noise

    # Filtere das Signal (cutoff = 30 Hz)
    filtered = hochpassfilter_fft(mixed_signal, cutoff_hz=30, fs=fs)
    
    # Analyse mit FFT
    fourier = np.fft.fft(filtered)
    
    # Das niederfrequente Rauschen (2 Hz) muss fast komplett weg sein und der Mittelwert der Amplituden sollte stark reduziert sein
    noise_energy_after = np.mean(np.abs(np.fft.fft(filtered - clean_signal))) / fs * 2
    amp_100hz = (np.abs(fourier[100]) / fs) * 2
    
    error = False
    
    if noise_energy_after < 0.1:
        print("[OK] Rauschen/Artefakte (2 Hz) erfolgreich entfernt.")
    else:
        print(f"[FEHLER] 2 Hz Rauschen ist noch präsent (Restenergie: {noise_energy_after:.3f})")
        error = True
        
    if amp_100hz > 0.4:
        print("[OK] Nutzsignal (100 Hz) erhalten.")
    else:
        print(f"[FEHLER] Nutzsignal (100 Hz) zu schwach (Amplitude: {amp_100hz:.3f})")
        error = True

    if not error:
        print("ERGEBNIS: AT-03 BESTANDEN!")
        print("30Hz Filter arbeitet korrekt (2Hz unterdrückt, 100Hz erhalten).")
    else:
        print("ERGEBNIS: AT-03 FEHLGESCHLAGEN!")
        print("Der Filter arbeitet nicht wie erwartet.")

if __name__ == "__main__":
    main()
