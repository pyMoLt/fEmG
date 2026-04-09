import platform
import bitalino
import time
import threading
import numpy as np
from collections import deque


# --- Gerätekonfiguration ---
# Bluetooth-Adresse des BITalino – hier zentral einstellen, nicht in jedem Skript.
# macOS:          "/dev/tty.BITalino-XX-XX"  (Gerätepfad)
# Windows/Linux:  "XX:XX:XX:XX:XX:XX"         (MAC-Adresse)
DEFAULT_ADDRESS = "/dev/tty.BITalino-4C-C9"

# Größe des Ringpuffers für den Streaming-Modus (Samples).
# 5000 Samples = 5 Sekunden bei 1000 Hz. Ältere Daten werden automatisch überschrieben.
BUFFER_SIZE = 5000


# BitalinoConnector kapselt die gesamte Kommunikation mit dem BITalino-Board.
# Das BITalino-Paket (bitalino.BITalino) ist is_blocking, heißt Aufrufe wie connect() oder
# read() können unbegrenzt hängen, falls das Gerät nicht antwortet. Um das zu umgehen,
# laufen kritische Operationen in eigenen Threads mit Timeout. (Empfehlung von Claude, ohne das kaum Funktion auf MacOs)
#
# Zwei Betriebsmodi:
# - Episode: start() + read_episode(n) -> liest einmalig n Samples (für plot_emg)
# - Stream:  start_stream() + read_latest(n). Zusätzlich wird dauerhaft Daten in einen Ringpuffer gesammelt (für mean_activity / is_active)

class BitalinoConnector:

    def __init__(self, address=None):
        # Adresse: None = Standardwert aus DEFAULT_ADDRESS 
        self.address = address if address is not None else DEFAULT_ADDRESS

        self.device    = None   # bitalino.BITalino-Objekt nach erfolgreicher Verbindung
        self.connected = False  # Bluetooth-Verbindung hergestellt?
        self.sampling  = False  # BITalino sendet gerade Daten?
        self._rate     = 1000   # zuletzt verwendete Sampling-Rate (für Neustart im Stream)
        self._channels = [0]    # zuletzt verwendete Kanäle

        # Stream-Zustand
        self._streaming     = False           # läuft der Hintergrund-Stream?
        self._stream_thread = None
        self._buffer        = deque(maxlen=BUFFER_SIZE)  # Ringpuffer: älteste Daten raus
        self._lock          = threading.Lock()           # schützt den Puffer vor Race Conditions

    # Stellt die Bluetooth-Verbindung her. Wird Nur einmal augefrufen.
    # Der Verbindungsaufbau läuft in einem Thread mit 15s Timeout,
    # damit das Hauptprogramm nicht einfriert, falls das Gerät nicht antwortet.
    def connect(self):
        if self.connected:
            print("[BITalino] Schon verbunden.")
            return True

        ergebnis = [None]
        fehler   = [None]

        def do_connect():
            try:
                ergebnis[0] = bitalino.BITalino(self.address)
            except Exception as e:
                fehler[0] = e

        print(f"[BITalino] Verbinde mit {self.address} ...")
        t = threading.Thread(target=do_connect, daemon=True)
        t.start()
        t.join(timeout=15)  # nach 15s aufgeben

        if t.is_alive():
            print("[BITalino] Timeout: Gerät antwortet nicht.")
            self.device = None
            self.connected = False
            return False
        if fehler[0]:
            print(f"[BITalino] Verbinden fehlgeschlagen: {fehler[0]}")
            self.device = None
            self.connected = False
            return False

        self.device    = ergebnis[0]
        self.connected = True
        print("[BITalino] Verbunden!")

        # macOS und Bluetooth SPP brauchen nach dem Verbinden eine kurze Stabilisierungsphase, sonst kommen fehlerhafte Bytes
        if platform.system() == "Darwin":
            self._macos_stabilize()
        return True

    # Startet die Datenerfassung auf dem BITalino.
    # Muss vor read_episode() oder start_stream() aufgerufen werden.
    # rate: Sampling-Rate in Hz (Standard: 1000 Hz laut Aufgabenstellung)
    # channels: Liste der aktiven Kanäle, [0] = A1 = EMG-Sensor
    def start(self, rate=1000, channels=None):
        if channels is None:
            channels = [0]
        if not self.device:
            print("[BITalino] Kein Gerät gefunden.")
            return False
        if self.sampling:
            return True  # läuft bereits
        self._rate     = rate
        self._channels = channels
        try:
            self.device.start(rate, channels)
            self.sampling = True
            print(f"[BITalino] Aufnahme gestartet ({rate} Hz, Kanäle: {channels}).")
            return True
        except Exception as e:
            print(f"[BITalino] Start fehlgeschlagen: {e}")
            return False

    # Liest einmalig n frische Samples (Episode-Modus für plot_emg).
    # Vor dem Aufruf muss start() aufgerufen worden sein.
    # Gibt ein numpy-Array zurück oder None bei Fehler.
    def read_episode(self, n=100):
        if not self.device or not self.sampling:
            print("[BITalino] Nicht bereit – start() zuerst aufrufen.")
            return None
        if self._streaming:
            print("[BITalino] Stream läuft – erst stop_stream() aufrufen.")
            return None

        # Empfangspuffer leeren damit wir wirklich frische Daten lesen
        self._drain()
        time.sleep(0.05)

        # Read im eigenen Thread, damit er bei einem Timeout abgebrochen werden kann
        result = [None]
        err    = [None]

        def do_read():
            try:
                result[0] = self.device.read(n)
            except Exception as e:
                err[0] = e

        t = threading.Thread(target=do_read, daemon=True)
        t.start()
        
        # Timeout dynamisch berechnen: Zeit für N Samples + 3 Sekunden Puffer
        dynamic_timeout = (n / self._rate) + 3.0
        t.join(timeout=dynamic_timeout)

        if t.is_alive():
            print("[BITalino] Read hängt. Gerät bitte prüfen.")
            return None
        if err[0]:
            print(f"[BITalino] Read-Fehler: {err[0]}")
            return None
        return result[0]

    # Startet den kontinuierlichen Stream-Modus (für mean_activity/is_active).
    # Ein Thread liest dauerhaft Daten in den Ringpuffer (_buffer). read_latest() kann dann jederzeit die neuesten Samples abrufen.
    # chunk: 20 Samples werden pro read aufgerufen
    def start_stream(self, rate=1000, channels=None, chunk=20):
        if channels is None:
            channels = [0]
        if self._streaming:
            print("[BITalino] Stream läuft bereits.")
            return True
        if not self.start(rate, channels):
            return False

        # Kurz warten und Puffer leeren: nach device.start() kommen auf macOS immer ein paar Bytes, die das erste Read verfälschen 
        time.sleep(0.15)
        self._drain()

        self._streaming = True

        def loop():
            while self._streaming:
                try:
                    data = self.device.read(chunk)
                    # Thread-sicher in den Ringpuffer schreiben
                    with self._lock:
                        for row in data:
                            self._buffer.append(row)
                except Exception as e:
                    print(f"[BITalino] Stream-Fehler: {e}")
                    if not self._streaming:
                        break
                    # Fehlerfall: Aufnahme kurz stoppen, Puffer leeren, neu starten
                    try:
                        self.device.stop()
                        self.device.started = False
                    except Exception:
                        pass
                    time.sleep(0.3)
                    self._drain()
                    try:
                        self.device.started = False
                        self.device.start(self._rate, self._channels)
                        time.sleep(0.15)
                        self._drain()
                    except Exception:
                        pass

        self._stream_thread = threading.Thread(target=loop, daemon=True)
        self._stream_thread.start()
        print(f"[BITalino] Stream läuft ({rate} Hz, Chunk: {chunk} Samples).")
        return True

    # Gibt die letzten n Samples aus dem Ringpuffer zurück.
    # Thread-sicher durch Lock. Gibt None zurück wenn noch nicht genug Daten im Puffer.
    def read_latest(self, n=100):
        with self._lock:
            buf = list(self._buffer)
        if len(buf) < n:
            return None
        return np.array(buf[-n:])

    # Stoppt den Stream-Thread und leert den Puffer.
    def stop_stream(self):
        self._streaming = False
        if self._stream_thread:
            self._stream_thread.join(timeout=2.0)
            self._stream_thread = None
        self.stop()
        with self._lock:
            self._buffer.clear()
        print("[BITalino] Stream gestoppt.")

    # Stoppt die Datenerfassung, lässt die Bluetooth-Verbindung aber offen.
    def stop(self):
        if not self.device:
            return
        try:
            self.device.stop()
            self.device.started = False
            self.sampling = False
            print("[BITalino] Aufnahme gestoppt.")
        except Exception as e:
            print(f"[BITalino] Stop-Fehler: {e}")
            self.sampling = False

    # Trennt die Verbindung vollständig: stoppt Stream/Aufnahme, schließt den Port.
    def close(self):
        if self._streaming:
            self.stop_stream()
        else:
            try:
                self.stop()
            except Exception:
                pass
        time.sleep(0.5)  # kurz warten damit der Port sauber freigegeben wird
        try:
            self.device.close()
        except Exception as e:
            print(f"[BITalino] Warnung beim Schließen: {e}")
        self.connected = False
        print("[BITalino] Verbindung getrennt.")

    # Liest alle ausstehenden Bytes aus dem Empfangspuffer weg.
    # Wir nutzen socket.read(), statt reset_input_buffer(), weil reset_input_buffer() auf macOS den Bluetooth-Datenstrom zerstört.
    def _drain(self):
        try:
            n = self.device.socket.in_waiting
            if n > 0:
                self.device.socket.read(n)
        except Exception:
            pass

    # Kurze Stabilisierungspause nach dem Verbinden auf macOS.
    # Bluetooth SPP unter macOS braucht ~0.5s bis der Datenstrom stabil ist.
    def _macos_stabilize(self):
        time.sleep(0.5)
        self._drain()
