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
        startTime = time.time()
        for filename in os.listdir(path):
            if filename.endswith('.png'):
                image_path = os.path.join(path, filename)
                image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                self.stingerImages.append(image)
        print(f"Stinger frames loaded in {time.time() - startTime:.6f} seconds")

    def _findAlphaInvertAndMerge(self, imageList):
        timeStart = time.time()
        for image in imageList:
            b, g, r, a = cv2.split(image)
            alpha = cv2.merge((a, a, a))

            ia = cv2.bitwise_not(a)
            invAlpha = cv2.merge((ia, ia, ia))
            self.stingerAlphaImages.append(alpha)
            self.stingerInvAlphaImages.append(invAlpha)
            self.stingerRGBImages.append(cv2.merge((b, g, r)))
        print(f"Alpha, Inverted Alpha and RGB frames found in {time.time() - timeStart:.6f} seconds")

    def _setPremultipliedFrame(self, imageList):
        timeStart = time.time()
        for image, alpha in zip(imageList, self.stingerAlphaImages):
            premultiplied = cv2.bitwise_and(image, alpha)
            self.stingerPreMultipliedImages.append(premultiplied)
        print(f"Premultiplied frames found in {time.time() - timeStart:.6f} seconds")
        print(f"Total frames: {len(self.stingerPreMultipliedImages)}")


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
        self.timer.start(1000 // 60)  # Update every 16.67ms (60 FPS)

    def updateFrame(self):
        foreground = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        if self.frames:

            frame = self.frames[self.currentIndex]
            ff = cv2.bitwise_and(foreground, self.loaderThread.stingerInvAlphaImages[self.currentIndex])
            result = cv2.add(ff, frame)
            height, width, channel = result.shape
            qImg = QImage(result.data, width, height, QImage.Format.Format_BGR888)
            self.label.setPixmap(QPixmap.fromImage(qImg))
            self.label.setScaledContents(True)
            self.label.resize(width, height)
            if self.currentIndex == 0:
                self.loopNumber = (self.loopNumber + 1) % 4


if __name__ == '__main__':
    app = QApplication([])

    path = r'/cap4/cap4_5/stingerDefault'
    loaderThread = StingerLoaderThread(path)

    stingerDisplay = StingerDisplay(loaderThread)
    stingerDisplay.show()

    loaderThread.start()

    app.exec()
