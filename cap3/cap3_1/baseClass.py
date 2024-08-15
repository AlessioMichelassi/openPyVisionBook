import time

import cv2
import numpy as np
from PyQt6.QtCore import QObject, QSize


class BaseClass(QObject):
    effectList = []
    _frame = None

    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        super().__init__()
        """
        Initializes the base class with a synchronization object and a resolution.
        Connects the synchronization signal to the capture_frame function.
        """
        # init object
        self.synch_Object = synchObject
        self.resolution = resolution
        self._frame = np.zeros((resolution.height(), resolution.width(), 3),
                               dtype=np.uint8)
        # init variables
        self.start_time = time.time()
        self.frame_count = 0
        self.total_time = 0
        self.fps = 0
        self.last_update_time = time.time()
        # init connections
        self.initConnections()

    def initConnections(self):
        """
        Initializes the connections between the synchronization object
            and the captureFrame function.
        """
        if self.synch_Object is not None:
            self.synch_Object.synch_SIGNAL.connect(self.captureFrame)

    def captureFrame(self):
        """
        This class is a base class for all frame processors.
        It captures a frame and updates the FPS value.
        :return:
        """
        self.updateFps()

    def getFrame(self):
        """
        Returns the current frame.
        :return:
        """
        if self._frame is None:
            return self.returnBlackFrame()
        return self._frame

    def updateFps(self):
        """
        Updates the FPS value.
        :return:
        """
        self.frame_count += 1
        current_time = time.time()
        elapsed_time = current_time - self.last_update_time
        if elapsed_time >= 1.0:  # Update FPS every second
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.last_update_time = current_time

    def returnBlackFrame(self):
        """
        Returns a black frame.
        """
        return np.zeros((self.resolution.height(), self.resolution.width(), 3),
                        dtype=np.uint8)


