import time

import numpy as np
from PyQt6.QtCore import *


class BlackGenerator(QObject):

    def __init__(self, resolution=QSize(1920, 1080), parent=None):
        super().__init__(parent)
        self._name = self.__class__.__name__
        self.resolution = resolution
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        self._resolution = resolution
        self.running = False  # Stato di esecuzione
        self.start_time = time.time()
        self.frame_count = 0
        self.total_time = 0
        self.fps = 0
        self.last_update_time = time.time()

    def captureFrame(self):
        pass

    def getFrame(self):
        return self._frame

    def startProcessing(self):
        self.running = True
        # Potresti voler eseguire del codice iniziale qui, se necessario

    def stop(self):
        self.running = False
        # Pulizia o altre operazioni di chiusura, se necessario

    def updateFps(self):
        self.frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        if elapsed_time >= 1.0:  # Update FPS every second
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.last_update_time = current_time

    def serialize(self):
        # Chiama il metodo serialize della classe base
        return {
            "class": "BlackGenerator",
            "name": "Black",
            "resolution": [self._resolution.width(), self._resolution.height()],
        }

    def deserialize(self, data):
        self._frame = np.zeros((self._resolution.height(), self._resolution.width(), 3), dtype=np.uint8)
