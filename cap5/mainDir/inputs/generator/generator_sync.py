import time

from PyQt6.QtCore import *


class SyncGenerator(QObject):
    sync_SIGNAL = pyqtSignal(name="syncSignal")

    def __init__(self, fps, parent=None):
        super().__init__(parent)
        self.fps = fps
        self.interval = 1000 // fps  # Intervallo in millisecondi
        self.syncThread = QThread()
        self.syncThread.run = self.run  # Definisci il metodo run
        self.syncThread.start()

    def run(self):
        while True:
            start_time = time.time()  # Inizia il timer
            self.sync_SIGNAL.emit()
            time_to_wait = max(0, self.interval / 1000 - (time.time() - start_time))
            QThread.msleep(int(time_to_wait * 1000))  # Aspetta fino al prossimo intervallo



