# Version: 2024.09.03


from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class CacheWorker(QThread):
    progressUpdated = pyqtSignal(int)
    operationCompleted = pyqtSignal()

    def __init__(self, cacheFunction, *args, **kwargs):
        super().__init__()
        self.cacheFunction = cacheFunction
        self.args = args
        self.kwargs = kwargs
        self._is_running = True

    def run(self):
        if self._is_running:
            self.cacheFunction(*self.args, **self.kwargs, progress_callback=self.progressUpdated)
            self.operationCompleted.emit()

    def stop(self):
        self._is_running = False
