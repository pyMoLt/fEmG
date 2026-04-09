# Zielerreichungsgrade (Goals)

Die persönliche Bewertung und Strukturierung des fEmG-Projekts orientiert sich an dieser Skala.

| Level | Kriterien zur Erreichung | Status |
| :--- | :--- | :---: |
| **Bronze** |- Die Bluetooth-Verbindung zum BITalino funktioniert und ist robust.<br>Rohdaten können mit 1000Hz via Stream ausgelesen werden.<br>- `adc_to_mv()` rechnet 10-bit Werte korrekt in Millivolt um.<br>- `plot_emg()` erzeugt einen Matplotlib-Plot mit drei Stufen (Roh, in mV, gefiltert). | Check.<br> CAVE: Unter MacOs Stabilitätsprobleme|
| **Silber** | - Alles aus Bronze erfüllt.<br>- Der 30Hz Hochpassfilter `hochpassfilter_fft()` basierend auf Fourier-Transformation funktioniert und ist im Code sauber dokumentiert.<br>- Es werden sauber Frequenzen von 0-30Hz abgeschnitten. | Check |
| **Gold** | - Alles aus Silber erfüllt.<br>- `mean_activity()` berechnet die Signalleistung der Muskelaktivität korrekt, und es wird die gewählte Methode detailliert dokumentiert.<br>- `is_active()` nutzt einen definierbaren Schwellenwert zur binären Klassifikation (boolean).<br>- Der `emg_tracker` merkt sich den stärksten Ausschlag und Flappy Bird reagiert in Echtzeit auf die Muskeln. | Check |
| **Platin** | - Alles aus Gold erfüllt.<br>- Die Codebasis ist aufgeräumt, strikt modular und konsistent. Alle Entscheidungen, wie RMS statt MAV, werden im Code begründet.<br>- Unit- und AT-Tests sind enthalten und bei Ausführung erfolgreich.<br>- Der 8-seitigen Analysebericht ist vorbereitet. | Check|
