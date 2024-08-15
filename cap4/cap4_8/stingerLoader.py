import os
import time

import cv2
from PyQt6.QtCore import *
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

