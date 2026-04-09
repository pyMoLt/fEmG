import bitalino
import numpy as np
from matplotlib import pyplot as plt

# TODO: Passen sie die 3 Methoden sowie den Konstruktor (__init__) der Klasse BioFeedback wie in den Aufgaben
#  beschrieben an. Sie können (und sollten) weitere Hilsmethoden anlegen. Ändern Sie nicht die Namen und Parameter
#  von is_active und mean_active. Die bereits importierten Pakete reichen für die Lösung aus. Sie können aber noch
#  zusätzlich scikit-learn importieren und nutzen. Weitere Pakete sind nicht zugelassen!

class BioFeedback:

    def __init__(self):
        self.device = 42


    def plot_emg(self):
        pass


    def is_active(self):
        pass


    def mean_activity(self):
        pass




    # Cleanup
    def close(self):
        self.device.stop()

    def __del__(self):
        self.close()



if __name__ == "__main__":
    BF = BioFeedback()
    BF.plot_emg()
    BF.close()