import os
import time
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import cv2
import numpy as np


class StingerLoaderThread(QThread):
    stingerReady = pyqtSignal()
    progressUpdated = pyqtSignal(int)  # Signal to update progress with a percentage value

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
        files = [f for f in os.listdir(path) if f.endswith('.png')]
        total_files = len(files)
        for idx, filename in enumerate(files):
            image_path = os.path.join(path, filename)
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            self.stingerImages.append(image)
            self.progressUpdated.emit(int((idx + 1) / total_files * 100))
        print(f"Stinger frames loaded in {time.time() - startTime:.6f} seconds")

    def _findAlphaInvertAndMerge(self, imageList):
        timeStart = time.time()
        total_images = len(imageList)
        for idx, image in enumerate(imageList):
            b, g, r, a = cv2.split(image)
            a = a / 255.0
            alpha = cv2.merge((a, a, a))
            invAlpha = cv2.merge((1 - a, 1 - a, 1 - a))
            self.stingerAlphaImages.append(alpha)
            self.stingerInvAlphaImages.append(invAlpha)
            self.stingerRGBImages.append(cv2.merge((b, g, r)))
            self.progressUpdated.emit(int((idx + 1) / total_images * 100))
        print(f"Alpha, Inverted Alpha and RGB frames found in {time.time() - timeStart:.6f} seconds")

    def _setPremultipliedFrame(self, imageList):
        timeStart = time.time()
        total_images = len(imageList)
        for idx, (image, alpha) in enumerate(zip(imageList, self.stingerAlphaImages)):
            premultiplied = cv2.multiply(image.astype(np.float32), alpha, dtype=cv2.CV_8U)
            self.stingerPreMultipliedImages.append(premultiplied)
            self.progressUpdated.emit(int((idx + 1) / total_images * 100))
        print(f"Premultiplied frames found in {time.time() - timeStart:.6f} seconds")
        print(f"Total frames: {len(self.stingerPreMultipliedImages)}")


class StingerDisplay(QWidget):
    def __init__(self, loaderThread, parent=None):
        super().__init__(parent)
        # init widgets
        self.loaderThread = loaderThread
        self.lblViewer = QLabel(self)
        self.lblTime = QLabel("Loading Stinger Frames...")
        self.lblMediaTime = QLabel("Time: 0.0s")
        self.progressBar = QProgressBar(self)
        self.vwr_timer = QTimer(self)
        self.prgBar_timer = QTimer(self)

        # init variables
        self.startTime = time.time()
        self.currentIndex = 0
        self.totalTimeSpent = 0
        self.mediaTimeSpend = 0
        self.mediaIndex = 0
        self.frames = []
        self.invMasks = []

        # init UI
        self.initUI()
        self.initGeometry()
        self.initStyle()
        self.initConnections()

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.lblViewer)
        timeLayout = QHBoxLayout()
        timeLayout.addWidget(self.lblTime)
        timeLayout.addWidget(self.lblMediaTime)
        timeLayout.addWidget(self.progressBar)
        mainLayout.addLayout(timeLayout)
        self.setLayout(mainLayout)

    def initConnections(self):
        self.loaderThread.stingerReady.connect(self.onStingerReady)
        self.loaderThread.progressUpdated.connect(self.updateProgressBar)
        self.vwr_timer.timeout.connect(self.updateFrame)
        self.prgBar_timer.timeout.connect(self.animateProgressBar)
        self.prgBar_timer.start(100)

    def initStyle(self):
        lblStyle = ("QLabel {"
                    "background-color: #000000;"
                    "color: #00FF00;"
                    "border: 1px solid #00FF00;"
                    "border-radius: 5px;}")
        self.lblViewer.setStyleSheet(lblStyle)

    def initGeometry(self):
        self.setGeometry(10, 50, 1920, 1080)
        self.progressBar.setRange(0, 100)

    @pyqtSlot(int)
    def updateProgressBar(self, value):
        self.progressBar.setValue(value)

    @pyqtSlot()
    def animateProgressBar(self):
        if self.progressBar.value() < 100:
            value = (self.progressBar.value() + 1) % 101
            self.progressBar.setValue(value)
        elapsed_time = time.time() - self.startTime
        self.lblMediaTime.setText(f"Time: {elapsed_time:.1f}s")

    @pyqtSlot()
    def onStingerReady(self):
        self.frames = self.loaderThread.stingerPreMultipliedImages
        self.invMasks = self.loaderThread.stingerInvAlphaImages
        self.vwr_timer.start(1000 // 60)  # Update every 16.67ms (60 FPS)
        self.prgBar_timer.stop()

    def updateFrame(self):
        program = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        if self.frames:
            timeStart = time.time()
            stinger_frame = self.frames[self.currentIndex]
            inv_mask = self.invMasks[self.currentIndex]
            program_masked = cv2.multiply(program, inv_mask, dtype=cv2.CV_8U)
            result = cv2.add(stinger_frame, program_masked)
            height, width, channel = result.shape
            qImg = QImage(result.data, width, height, QImage.Format.Format_BGR888)
            self.lblViewer.setPixmap(QPixmap.fromImage(qImg))
            self.lblViewer.setScaledContents(True)
            self.lblViewer.resize(width, height)
            self.currentIndex = (self.currentIndex + 1) % len(self.frames)
            self.lblTime.setText(f"Time: {time.time() - timeStart:.6f}")
            self.updateMediaTime(timeStart)

    def updateMediaTime(self, timeStart):
        endTime = time.time() - timeStart
        self.totalTimeSpent += endTime
        self.mediaIndex += 1
        self.mediaTimeSpend = self.totalTimeSpent / self.mediaIndex
        self.lblTime.setText(f"Time: {endTime:.6f}")
        self.lblMediaTime.setText(f"Media Time: {self.mediaTimeSpend:.6f}")

    def closeEvent(self, event):
        print(f"Media Time: {self.mediaTimeSpend:.6f}")
        self.vwr_timer.stop()
        event.accept()


if __name__ == '__main__':
    app = QApplication([])

    path = r'C:\pythonCode\openPyVisionBook\openPyVisionBook\cap5\cap5_5\stingerTest'
    loaderThread = StingerLoaderThread(path)
    stingerDisplay = StingerDisplay(loaderThread)
    stingerDisplay.show()

    loaderThread.start()

    app.exec()

