import time

import cv2
import numpy as np
from PyQt6.QtCore import QObject, QSize


class BaseClassExtended(QObject):
    clip_limit = 2.0
    tile_grid_size = (4, 4)
    gamma = 1.0
    isFrameInverted = False
    isFrameAutoScreen = False
    isFrameCLAHE = False
    isFrameHistogramEqualization = False
    isFrameCLAHEYUV = False
    isFrameHistogramEqualizationYUV = False

    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        super().__init__()
        self.synch_Object = synchObject
        self.resolution = resolution
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        if self.synch_Object is not None:
            self.synch_Object.synch_SIGNAL.connect(self.captureFrame)
        self.start_time = time.time()
        self.frame_count = 0
        self.total_time = 0
        self.fps = 0
        self.last_update_time = time.time()

    def captureFrame(self):
        self.updateFps()

    def getFrame(self):
        return self.frameProcessor(self._frame)

    def frameProcessor(self, frame):
        if self.isFrameInverted:
            frame = self.invertFrame(frame)
        if self.isFrameAutoScreen:
            frame = self.autoScreenFrame(frame)
        if self.isFrameCLAHE:
            frame = self.applyCLAHE(frame, self.clip_limit, self.tile_grid_size)
        if self.isFrameHistogramEqualization:
            frame = self.applyHistogramEqualization(frame)
        if self.isFrameCLAHEYUV:
            frame = self.applyCLAHEYUV(frame, self.clip_limit, self.tile_grid_size)
        if self.isFrameHistogramEqualizationYUV:
            frame = self.applyHistogramEqualizationYUV(frame)
        if self.gamma != 1.0:
            frame = self.applyGammaByLut(frame, self.gamma)
        return frame

    def updateFps(self):
        self.frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        if elapsed_time >= 1.0:  # Update FPS every second
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.last_update_time = current_time
            # print(f"Updated FPS: {self.fps:.2f}")  # Debug output

    @staticmethod
    def invertFrame(image):
        """
        Inverts the frame colors.
        """
        return cv2.bitwise_not(image)

    @staticmethod
    def autoScreenFrame(image):
        """
        Automatically creates a screen frame.
        """
        inv1 = cv2.bitwise_not(image)
        mult = cv2.multiply(inv1, inv1, scale=1.0 / 255.0)
        return cv2.bitwise_not(mult).astype(np.uint8)

    @staticmethod
    def getRGBChannels(frame):
        """
        Returns the RGB channels of a frame.
        """
        return cv2.split(frame)

    @staticmethod
    def setRGBChannels(channels):
        """
        Sets the RGB channels of a frame.
        """
        return cv2.merge(channels)

    @staticmethod
    def applyGammaByLut(image, gamma):
        inv_gamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** inv_gamma * 255
                          for i in range(256)]).astype(np.uint8)
        return cv2.LUT(image, table)

    @staticmethod
    def applyCLAHE(image, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        Applies the Contrast Limited Adaptive Histogram Equalization (CLAHE) to the image.
        """
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        return clahe.apply(image)

    @staticmethod
    def applyHistogramEqualization(image):
        """
        Applies the Histogram Equalization to the image.
        """
        return cv2.equalizeHist(image)

    @staticmethod
    def applyCLAHEYUV(image, clip_limit=2.0, tile_grid_size=(8, 8)):
        """
        Applies the Contrast Limited Adaptive Histogram Equalization (CLAHE) to the Y channel of the YUV image.
        """
        yuv_img = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
        yuv_img[:, :, 0] = clahe.apply(yuv_img[:, :, 0])
        return cv2.cvtColor(yuv_img, cv2.COLOR_YUV2BGR)


    @staticmethod
    def applyHistogramEqualizationYUV(image):
        """
        Applies the Histogram Equalization to the Y channel of the YUV image.
        """
        yuv_img = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
        yuv_img[:, :, 0] = cv2.equalizeHist(yuv_img[:, :, 0])
        return cv2.cvtColor(yuv_img, cv2.COLOR_YUV2BGR)


