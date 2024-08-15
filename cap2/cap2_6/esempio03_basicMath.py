import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from cap2.cap2_6.synchObject import SynchObject


class TestNumpy(QObject):

    def __init__(self, synch, parent=None):
        super().__init__(parent)
        self._frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
        self.synch = synch
        self.synch.synch_SIGNAL.connect(self.captureFrame)

    def captureFrame(self):
        self._frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)

    def getFrame(self):
        return self._frame


class VideoApp(QWidget):

    def __init__(self, synch, test, parent=None):
        super().__init__(parent)
        self.lblViewer = QLabel()
        self.synch = synch
        self.test = test
        self.synch.synch_SIGNAL.connect(self.updateViewer)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.lblViewer)
        self.setLayout(self.layout)  # Applica il layout alla finestra

    def updateViewer(self):
        frame = self.test.getFrame()
        frame = 1 / (1 + np.exp(-10 * (frame - 0.5)))

        qImage = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_RGB888)
        self.lblViewer.setPixmap(QPixmap.fromImage(qImage))


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    synch = SynchObject(60)
    test = TestNumpy(synch)
    video = VideoApp(synch, test)
    video.show()
    sys.exit(app.exec())
