import os
import time
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
import cv2
import numpy as np


class StingerLoaderThread(QThread):
    stingerReady = pyqtSignal()
    progressUpdated = pyqtSignal(int)  # Signal to update progress with a percentage value
    somethingDone = pyqtSignal(str, str)

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
        startTime = time.time()
        files = [f for f in os.listdir(_path) if f.endswith('.png')]
        total_files = len(files)
        for idx, filename in enumerate(files):
            image_path = os.path.join(_path, filename)
            image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
            self.stingerImages.append(image)
            self.progressUpdated.emit(int((idx + 1) / total_files * 100))
        print(f"Stinger frames loaded in {time.time() - startTime:.6f} seconds")
        returnString = f"Stinger frames loaded in {time.time() - startTime:.6f} seconds"
        endTime = time.time() - startTime
        self.somethingDone.emit(returnString, f"{endTime:.6f}")

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
        returnString = f"Alpha, Inverted Alpha and RGB frames found in {time.time() - timeStart:.6f} seconds"
        endTime = time.time() - timeStart
        self.somethingDone.emit(returnString, f"{endTime:.6f}")

    def _setPremultipliedFrame(self, imageList):
        timeStart = time.time()
        total_images = len(imageList)
        for idx, (image, alpha) in enumerate(zip(imageList, self.stingerAlphaImages)):
            premultiplied = cv2.multiply(image.astype(np.float32), alpha, dtype=cv2.CV_8U)
            self.stingerPreMultipliedImages.append(premultiplied)
            self.progressUpdated.emit(int((idx + 1) / total_images * 100))
        returnString = f"Premultiplied frames found in {time.time() - timeStart:.6f} seconds"
        endTime = time.time() - timeStart
        self.somethingDone.emit(returnString, f"{endTime:.6f}")

        print(f"Total frames: {len(self.stingerPreMultipliedImages)}")


class GLImageWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage()

    def setImage(self, image):
        self.image = image
        self.update()

    def paintGL(self):
        if not self.image.isNull():
            painter = QPainter(self)
            painter.drawImage(self.rect(), self.image)
            painter.end()


class StingerDisplay(QWidget):
    floatCount = 0

    def __init__(self, _loaderThread, parent=None):
        super().__init__(parent)
        # init widgets
        self.loaderThread = _loaderThread
        self.glWidget = GLImageWidget(self)
        self.lblTime = QLabel("Time: 0.0")
        self.lblMediaTime = QLabel("Media Time: 0.0")
        self.prgBar = QProgressBar(self)
        self.timer = QTimer(self)
        self.prgBar_timer = QTimer(self)
        # init variables
        self.startTime = time.time()
        self.currentIndex = 0
        self.totalTimeSpent = 0
        self.mediaTimeSpend = 0
        self.mediaIndex = 0
        self.frames = []
        self.invMasks = []
        self.qImg = QImage(1920, 1080, QImage.Format.Format_BGR888)
        # init UI
        self.initUI()
        self.initGeometry()
        self.initStyle()
        self.initConnections()

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.glWidget)
        timeLayout = QHBoxLayout()
        timeLayout.addWidget(self.lblTime)
        timeLayout.addWidget(self.lblMediaTime)
        timeLayout.addWidget(self.prgBar)
        mainLayout.addLayout(timeLayout)
        self.setLayout(mainLayout)

    def initStyle(self):
        lblStyle = ("QLabel {"
                    "background-color: #000000;"
                    "color: #00FF00;"
                    "border: 1px solid #00FF00;"
                    "border-radius: 5px;}")
        self.glWidget.setStyleSheet(lblStyle)
        self.prgBar.setMaximum(100)

    def initGeometry(self):
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowTitle('Stinger Display')
        self.glWidget.setFixedSize(1920, 1080)

    def initConnections(self):
        self.loaderThread.stingerReady.connect(self.onStingerReady)
        self.loaderThread.progressUpdated.connect(self.updateProgressBar)
        self.loaderThread.somethingDone.connect(self.updateProgressBarText)
        self.timer.timeout.connect(self.updateFrame)
        self.prgBar_timer.timeout.connect(self.animateProgressBar)
        self.prgBar_timer.start(100)

    @pyqtSlot(int)
    def updateProgressBar(self, value):
        self.prgBar.setValue(value)

    @pyqtSlot()
    def animateProgressBar(self):
        if self.prgBar.value() < 100:
            value = (self.prgBar.value() + 1) % 101
            self.prgBar.setValue(value)
        elapsed_time = time.time() - self.startTime
        self.lblMediaTime.setText(f"Time: {elapsed_time:.1f}s")

    @pyqtSlot(str, str)
    def updateProgressBarText(self, returnString, timeString):
        print(f"{returnString} in {timeString} seconds")
        self.floatCount += float(timeString)
        if self.prgBar.value() >= 100:
            self.prgBar.setValue(100)
            self.prgBar_timer.stop()

    @pyqtSlot()
    def onStingerReady(self):
        self.frames = self.loaderThread.stingerPreMultipliedImages
        self.invMasks = self.loaderThread.stingerInvAlphaImages
        self.timer.start(1000 // 60)  # Update every 16.67ms (60 FPS)
        self.prgBar_timer.stop()

    def updateFrame(self):
        program = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        if self.frames:
            timeStart = time.time()
            stinger_frame = self.frames[self.currentIndex]
            inv_mask = self.invMasks[self.currentIndex]
            program_masked = cv2.multiply(program, inv_mask, dtype=cv2.CV_8U)
            result = cv2.add(stinger_frame, program_masked)
            result_contiguous = np.ascontiguousarray(result)  # Ensure the array is contiguous
            height, width, channel = result_contiguous.shape
            self.qImg = QImage(result_contiguous.data, width, height, QImage.Format.Format_BGR888)
            self.glWidget.setImage(self.qImg)
            self.currentIndex = (self.currentIndex + 1) % len(self.frames)
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
        self.timer.stop()
        event.accept()


if __name__ == '__main__':
    app = QApplication([])
    path = r'C:\pythonCode\openPyVisionBook\openPyVisionBook\cap5\cap5_5_StingerIdea\stingerTest'
    loaderThread = StingerLoaderThread(path)

    stingerDisplay = StingerDisplay(loaderThread)
    stingerDisplay.show()

    loaderThread.start()

    app.exec()
