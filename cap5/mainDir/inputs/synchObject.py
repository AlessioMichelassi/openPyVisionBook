from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class SynchObject(QObject):
    synch_SIGNAL = pyqtSignal()

    def __init__(self, fps=60, parent=None):  # Set FPS to 60
        super().__init__(parent)
        self.fps = fps
        self.syncTimer = QTimer(self)
        self.syncTimer.timeout.connect(self.sync)
        self.syncTimer.start(1000 // fps)
        self._initialized = True

    def sync(self):
        self.synch_SIGNAL.emit()
