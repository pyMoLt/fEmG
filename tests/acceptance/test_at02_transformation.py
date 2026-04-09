# AT-02: Signal-Transformation (ADC zu Millivolt)
#
# Prüft ob adc_zu_mv() korrekt rechnet: Der Mittelpunkt (ADC=512) muss
# 0 mV ergeben, und die Extremwerte (0 / 1023) müssen bei ca. ±1.64 mV liegen.
# Laut BITalino-Datenblatt ist der Ausgabebereich [-1.64 mV, +1.64 mV].
#
# Starten: python tests/acceptance/test_at02_transformation.py
import sys
import os
import numpy as np

# Den Pfad anpassen, damit wir src finden
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.utils.signal_proc import adc_to_mv

def main():
    print("AT-02: Signal-Transformation (Rohdaten zu mV)")
    
    # Testdaten: 0 (Min), 512 (Mitte), 1023 (Max)
    test_values = {
        0:    -1.64,
        # Bei 512 erwarten wir fast 0. (512/1024 - 0.5) = 0.0
        512:   0.00,
        1023:  1.64
    }

    error = False
    for adc, expected in test_values.items():
        # Formel aufrufen
        mv = adc_to_mv(np.array([adc]))[0]
        
        if abs(mv - expected) > 0.05:
            print(f"[FEHLER] ADC {adc:4d} ergab {mv:+.3f} mV (erwartet: ca. {expected:+.3f} mV)")
            error = True
        else:
            print(f"[OK] ADC {adc:4d} ergab {mv:+.3f} mV")

    if not error:
        print("ERGEBNIS: AT-02 BESTANDEN!")
        print("Die Umrechnung entspricht den Erwartungen.")
    else:
        print("ERGEBNIS: AT-02 FEHLGESCHLAGEN!")
        print("Die Werte liegen außerhalb des Erwartungsbereichs.")

if __name__ == "__main__":
    main()
