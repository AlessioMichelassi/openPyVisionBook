import os
import time
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import cv2
import numpy as np
import ctypes

class StingerLoaderThread(QThread):
    stingerReady = pyqtSignal()
    somethingDone = pyqtSignal(str)

    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.stingerImages = []
        self.stingerRGBImages = []
        self.stingerAlphaImages = []
        self.stingerInvAlphaImages = []
        self.stingerPreMultipliedImages = []
        self.shared_memory = QSharedMemory("ImageData")
        self.shared_memory.create(1920 * 1080 * 3)

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
        self.somethingDone.emit(f"{time.time() - startTime:.6f}")

    def _findAlphaInvertAndMerge(self, imageList):
        startTime = time.time()
        for image in imageList:
            b, g, r, a = cv2.split(image)
            a = a / 255.0
            alpha = cv2.merge((a, a, a))
            invAlpha = cv2.merge((1 - a, 1 - a, 1 - a))
            self.stingerAlphaImages.append(alpha)
            self.stingerInvAlphaImages.append(invAlpha)
            self.stingerRGBImages.append(cv2.merge((b, g, r)))
        print(f"Alpha, Inverted Alpha and RGB frames found in {time.time() - startTime:.6f} seconds")
        self.somethingDone.emit(f"{time.time() - startTime:.6f}")

    def _setPremultipliedFrame(self, imageList):
        startTime = time.time()
        for image, alpha in zip(imageList, self.stingerAlphaImages):
            premultiplied = cv2.multiply(image.astype(np.float32), alpha, dtype=cv2.CV_8U)
            self.stingerPreMultipliedImages.append(premultiplied)
            self.somethingDone.emit(f"{time.time() - startTime:.6f}")
        print(f"Premultiplied frames found in {time.time() - startTime:.6f} seconds")
        print(f"Total frames: {len(self.stingerPreMultipliedImages)}")
        self.somethingDone.emit(f"{time.time() - startTime:.6f}")


class StingerDisplay(QWidget):
    def __init__(self, loaderThread, parent=None):
        super().__init__(parent)
        # init widgets
        self.loaderThread = loaderThread
        self.lblViewer = QLabel(self)
        self.lblTime = QLabel("Time: 0.0")
        self.lblMediaTime = QLabel("Media Time: 0.0")
        self.prgBar = QProgressBar(self)
        self.timer = QTimer(self)
        # init variables
        self.currentIndex = 0
        self.totalTimeSpent = 0
        self.mediaTimeSpend = 0
        self.mediaIndex = 0
        self.frames = []
        self.invMasks = []
        self.shared_memory = QSharedMemory("ImageData")
        self.shared_memory.attach()
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
        timeLayout.addWidget(self.prgBar)
        mainLayout.addLayout(timeLayout)
        self.setLayout(mainLayout)

    def initStyle(self):
        lblStyle = ("QLabel {"
                    "background-color: #000000;"
                    "color: #00FF00;"
                    "border: 1px solid #00FF00;"
                    "border-radius: 5px;}")
        self.lblViewer.setStyleSheet(lblStyle)
        self.prgBar.setMaximum(20)

    def initGeometry(self):
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowTitle('Stinger Display')
        self.lblViewer.setFixedSize(1920, 1080)

    def initConnections(self):
        self.loaderThread.stingerReady.connect(self.onStingerReady)
        self.loaderThread.somethingDone.connect(self.updateProgressBar)
        self.timer.timeout.connect(self.updateFrame)

    @pyqtSlot()
    def onStingerReady(self):
        self.frames = self.loaderThread.stingerPreMultipliedImages
        self.invMasks = self.loaderThread.stingerInvAlphaImages
        self.timer.start(1000 // 60)  # Update every 16.67ms (60 FPS)

    def updateFrame(self):
        program = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
        if self.frames:
            timeStart = time.time()
            stinger_frame = self.frames[self.currentIndex]
            inv_mask = self.invMasks[self.currentIndex]
            program_masked = cv2.multiply(program, inv_mask, dtype=cv2.CV_8U)
            result = cv2.add(stinger_frame, program_masked)
            self.shared_memory.lock()
            mem_ptr = ctypes.cast(int(self.shared_memory.data()), ctypes.POINTER(ctypes.c_char))
            ctypes.memmove(mem_ptr, result.ctypes.data, result.nbytes)
            self.shared_memory.unlock()
            qImg = QImage(self.shared_memory.data(), result.shape[1], result.shape[0], QImage.Format.Format_BGR888)
            self.lblViewer.setPixmap(QPixmap.fromImage(qImg))
            self.lblViewer.setScaledContents(True)
            self.lblViewer.resize(result.shape[1], result.shape[0])
            self.currentIndex = (self.currentIndex + 1) % len(self.frames)
            self.updateMediaTime(timeStart)

    def updateMediaTime(self, timeStart):
        endTime = time.time() - timeStart
        self.totalTimeSpent += endTime
        self.mediaIndex += 1
        self.mediaTimeSpend = self.totalTimeSpent / self.mediaIndex
        self.lblTime.setText(f"Time: {endTime:.6f}")
        self.lblMediaTime.setText(f"Media Time: {self.mediaTimeSpend:.6f}")

    def updateProgressBar(self, timeSpent):
        value = self.prgBar.value() + 1
        self.prgBar.setValue(value)

    def closeEvent(self, event):
        print(f"Media Time: {self.mediaTimeSpend:.6f}")
        self.timer.stop()
        event.accept()


if __name__ == '__main__':
    app = QApplication([])
    path = r'C:\pythonCode\openPyVisionBook\openPyVisionBook\cap5\cap5_5\stingerTest'
    loaderThread = StingerLoaderThread(path)
    # 0.008373

    stingerDisplay = StingerDisplay(loaderThread)
    stingerDisplay.show()

    loaderThread.start()

    app.exec()
