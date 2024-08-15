import os
import time
import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class StingerLoaderThread(QThread):
    stingerReady = pyqtSignal()
    progressUpdated = pyqtSignal()

    def __init__(self, _path, parent=None):
        super().__init__(parent)
        self.path = _path
        self.stingerImages = []
        self.stingerRGBImages = []
        self.stingerAlphaImages = []
        self.stingerInvAlphaImages = []
        self.stingerPreMultipliedImages = []

    def run(self):
        self.loadStingerFrames(self.path)
        self._findAlphaInvertAndMerge(self.stingerImages)
        self._setPremultipliedFrame(self.stingerRGBImages)
        self.stingerReady.emit()

    def loadStingerFrames(self, _path):
        for filename in os.listdir(_path):
            if filename.endswith('.png'):
                image_path = os.path.join(_path, filename)
                image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                self.stingerImages.append(image)
                self.progressUpdated.emit()

    def _findAlphaInvertAndMerge(self, imageList):
        for image in imageList:
            b, g, r, a = cv2.split(image)
            a = a / 255.0
            alpha = cv2.merge((a, a, a))
            invAlpha = cv2.merge((1 - a, 1 - a, 1 - a))
            self.stingerAlphaImages.append(alpha)
            self.stingerInvAlphaImages.append(invAlpha)
            self.stingerRGBImages.append(cv2.merge((b, g, r)))
            self.progressUpdated.emit()

    def _setPremultipliedFrame(self, imageList):
        for image, alpha in zip(imageList, self.stingerAlphaImages):
            premultiplied = cv2.multiply(image.astype(np.float32), alpha, dtype=cv2.CV_8U)
            self.stingerPreMultipliedImages.append(premultiplied)
            self.progressUpdated.emit()


class StingerDisplay(QWidget):
    def __init__(self, loaderThread, parent=None):
        super().__init__(parent)
        self.loaderThread = loaderThread
        self.progressBar = QProgressBar(self)
        self.lbl = QLabel("Loading Stinger Frames...", self)
        self.timeLabel = QLabel("Time: 0.0s", self)
        self.timer = QTimer(self)
        self.startTime = time.time()
        self.initUI()
        self.initConnections()
        self.loaderThread.start()
        self.timer.start(100)

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.lbl)
        mainLayout.addWidget(self.progressBar)
        mainLayout.addWidget(self.timeLabel)
        self.setLayout(mainLayout)
        self.setWindowTitle('Stinger Loader Progress')
        self.progressBar.setRange(0, 100)

    def initConnections(self):
        self.loaderThread.progressUpdated.connect(self.updateProgressBar)
        self.loaderThread.stingerReady.connect(self.onStingerReady)
        self.timer.timeout.connect(self.animateProgressBar)

    @pyqtSlot()
    def updateProgressBar(self):
        pass  # La progress bar viene animata dal timer

    @pyqtSlot()
    def animateProgressBar(self):
        value = (self.progressBar.value() + 1) % 101
        self.progressBar.setValue(value)
        elapsed_time = time.time() - self.startTime
        self.timeLabel.setText(f"Time: {elapsed_time:.1f}s")

    @pyqtSlot()
    def onStingerReady(self):
        self.timer.stop()
        self.progressBar.setValue(100)
        elapsed_time = time.time() - self.startTime
        self.timeLabel.setText(f"Completed in: {elapsed_time:.1f}s")
        print("All done!")


if __name__ == '__main__':
    path = r'C:\pythonCode\openPyVisionBook\openPyVisionBook\cap4\cap4_5\stingerTest'
    stingerLoaderThread = StingerLoaderThread(path)
    app = QApplication([])
    time.sleep(20)
    stingerDisplay = StingerDisplay(stingerLoaderThread)
    stingerDisplay.show()



    app.exec()
