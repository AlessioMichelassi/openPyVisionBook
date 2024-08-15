import os
import time
from PyQt6.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, QTimer
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
import cv2
import numpy as np


class StingerLoaderThread(QThread):
    stingerReady = pyqtSignal()

    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
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

    def loadStingerFrames(self, path):
        for filename in os.listdir(path):
            if filename.endswith('.png'):
                image_path = os.path.join(path, filename)
                image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                self.stingerImages.append(image)

    def _findAlphaInvertAndMerge(self, imageList):
        for image in imageList:
            b, g, r, a = cv2.split(image)
            alpha = cv2.merge((a, a, a))
            invAlpha = cv2.merge((cv2.bitwise_not(a), cv2.bitwise_not(a), cv2.bitwise_not(a)))
            self.stingerAlphaImages.append(alpha)
            self.stingerInvAlphaImages.append(invAlpha)
            self.stingerRGBImages.append(cv2.merge((b, g, r)))

    def _setPremultipliedFrameOLD(self, imageList):
        for image, alpha in zip(imageList, self.stingerAlphaImages):
            premultiplied = cv2.multiply(alpha, image)
            self.stingerPreMultipliedImages.append(premultiplied)

    def _setPremultipliedFrame(self, imageList):
        for image, alpha in zip(imageList, self.stingerAlphaImages):
            premultiplied = cv2.bitwise_and(image, image)
            self.stingerPreMultipliedImages.append(premultiplied)


class StingerDisplay(QWidget):
    def __init__(self, loaderThread, parent=None):
        super().__init__(parent)
        self.loopNumber = 0
        self.loaderThread = loaderThread
        self.loaderThread.stingerReady.connect(self.onStingerReady)
        self.label = QLabel(self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.currentIndex = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)

    @pyqtSlot()
    def onStingerReady(self):
        self.frames = self.loaderThread.stingerPreMultipliedImages
        self.timer.start(1000 // 60)  # Update every 100ms

    def updateFrame(self):
        if self.frames:
            if self.loopNumber == 0:
                frame = self.loaderThread.stingerPreMultipliedImages[self.currentIndex]
                self.setWindowTitle(f"premultiplied frame {self.currentIndex}")
            elif self.loopNumber == 1:
                frame = self.loaderThread.stingerRGBImages[self.currentIndex]
                self.setWindowTitle(f"RGB frame {self.currentIndex}")
            elif self.loopNumber == 2:
                frame = self.loaderThread.stingerAlphaImages[self.currentIndex]
                self.setWindowTitle(f"Alpha frame {self.currentIndex}")
            elif self.loopNumber == 3:
                frame = self.loaderThread.stingerInvAlphaImages[self.currentIndex]
                self.setWindowTitle(f"Inv Alpha frame {self.currentIndex}")
            self.currentIndex = (self.currentIndex + 1) % len(self.frames)
            height, width, channel = frame.shape
            qImg = QImage(frame.data, width, height, QImage.Format.Format_BGR888)
            self.label.setPixmap(QPixmap.fromImage(qImg))
            self.label.setScaledContents(True)
            self.label.resize(width, height)
            if self.currentIndex == 0:
                self.loopNumber = (self.loopNumber + 1) % 4


if __name__ == '__main__':
    app = QApplication([])

    path = r'C:\pythonCode\openPyVisionBook\openPyVisionBook\cap5\cap5_5\stingerTest'
    loaderThread = StingerLoaderThread(path)
    stingerDisplay = StingerDisplay(loaderThread)
    stingerDisplay.show()
    loaderThread.start()

    app.exec()
