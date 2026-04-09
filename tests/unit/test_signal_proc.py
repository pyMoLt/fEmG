# Unit-Tests für signal_proc.py
# Diese Tests laufen vollautomatisch ohne Hardware. Sie prüfen, ob Signalverarbeitungsfunktionen mathematisch korrekt implementiert sind.
# Starten: python tests/unit/test_signal_proc.py

import unittest
import numpy as np
import sys
import os

# Anhängen src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.utils.signal_proc import adc_to_mv, hochpassfilter_fft, rms

class TestSignalProc(unittest.TestCase):

    # Prüft die ADC zu mV-Umrechnung.
    # ADC=512 (Mittelpunkt des 10-bit Bereichs) muss ca. 0 mV ergeben.
    # ADC=0 und ADC=1023 müssen ca. ±1.64 mV ergeben (laut BITalino-Datenblatt).
    def test_adc_to_mv(self):
        # Mittelpunkt zu 0 mV
        zero_point = adc_to_mv(512)
        self.assertAlmostEqual(zero_point, 0.0, places=2)

        # Extremwerte bei ca. ±1.64 mV
        value_0    = adc_to_mv(0)
        value_1023 = adc_to_mv(1023)
        self.assertTrue(-1.7 < value_0    < -1.5)
        self.assertTrue( 1.5 < value_1023 <  1.7)

    # Prüft den 30 Hz Hochpassfilter.
    # Testsignal: 10 Hz (Störung) + 100 Hz (Nutzsignal).
    # Nach dem Filter muss 10hz nahezu verschwunden, 100 Hz erhalten bleiben.
    def test_hochpassfilter(self):
        fs = 1000
        t  = np.linspace(0, 1, fs)
        signal_10hz  = np.sin(2 * np.pi * 10  * t)
        signal_100hz = np.sin(2 * np.pi * 100 * t)
        mixed_signal   = signal_10hz + signal_100hz

        filtered_signal  = hochpassfilter_fft(mixed_signal, cutoff_hz=30, fs=fs)
        freq       = np.fft.fft(filtered_signal)
        freqs      = np.fft.fftfreq(len(filtered_signal), d=1/fs)

        amp_10hz  = np.abs(freq[10])  / fs
        amp_100hz = np.abs(freq[100]) / fs

        self.assertLess(amp_10hz,    0.01)  # Störung fast weg
        self.assertGreater(amp_100hz, 0.4)  # Nutzsignal erhalten

    # Prüft den RMS-Wert mit bekannten Ergebnissen.
    # Konstantes Signal: RMS muss genau 1 sein.
    # Sinussignal: RMS = 1/sqrt(2) = ca. 0.707.
    def test_rms(self):
        # Konstant => 1
        signal = np.array([1, 1, 1, 1])
        self.assertEqual(rms(signal), 1.0)

        # Sinus => 0.707
        t     = np.linspace(0, 1, 1000)
        sinus = np.sin(2 * np.pi * 50 * t)
        self.assertAlmostEqual(rms(sinus), 0.707, places=2)


if __name__ == '__main__':
    unittest.main()
