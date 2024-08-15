import os
import time
import cv2
import numpy as np
from PyQt6.QtCore import QObject


class StingerInputLoader(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stingerPath = ''
        self.stingerImages = []  # original list of images with alpha channel
        self.stingerRGBImages = []  # list of images without alpha channel
        self.stingerAlphaImages = []  # list of alpha channel images
        self.stingerInvAlphaImages = []  # list of inverted alpha channel images
        self.stingerPreMultipliedImages = []  # list of pre-multiplied images

    def setPath(self, path):
        self.stingerPath = path
        self.loadStingerFrames(path)
        self._findAlphaInvertAndMerge(self.stingerImages)

    def getStingerFrame(self, index):
        return self.stingerImages[index]

    def getStingerAlphaFrame(self, index):
        return self.stingerAlphaImages[index]

    def getStingerInvAlphaFrame(self, index):
        return self.stingerInvAlphaImages[index]

    def getStingerPremultipliedFrame(self, index):
        return self.stingerPreMultipliedImages[index]

    def _findAlphaInvertAndMerge(self, imageList):
        for image in imageList:
            b, g, r, a = cv2.split(image)
            alpha = cv2.merge((a, a, a))
            invA = cv2.bitwise_not(a)
            invAlpha = cv2.merge((invA, invA, invA))
            bgr = cv2.merge((b, g, r))
            self.stingerAlphaImages.append(alpha)
            self.stingerInvAlphaImages.append(invAlpha)
            self.stingerRGBImages.append(bgr)
            self.stingerPreMultipliedImages.append(cv2.multiply(alpha, bgr))

    def loadStingerFrames(self, path):
        for filename in os.listdir(path):
            if filename.endswith('.png'):
                image_path = os.path.join(path, filename)
                image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
                self.stingerImages.append(image)


if __name__ == '__main__':
    path = r'C:\pythonCode\openPyVisionBook\openPyVisionBook\cap4\cap4_5\stingerTest'
    stingerInputLoader = StingerInputLoader()

    timeStart = time.time()
    stingerInputLoader.setPath(path)
    print(f"Time to load stinger frames: {time.time() - timeStart} seconds")
