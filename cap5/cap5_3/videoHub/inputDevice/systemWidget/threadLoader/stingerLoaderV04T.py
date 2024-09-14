# Version: 2024.09.03
import logging
import os
import json
import time
import cv2
import numpy as np
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class StingerLoaderV04T(QThread):
    stingerReady = pyqtSignal()
    progressUpdated = pyqtSignal(int)

    def __init__(self, _path, parent=None):
        super().__init__(parent)
        self.path = _path
        self.stingerPreMultipliedImages = []
        self.stingerInvAlphaImages = []
        self._is_running = True

    def run(self):
        asyncio.run(self.loadAndProcessStingerFrames())

    async def loadAndProcessStingerFrames(self):
        loop = asyncio.get_running_loop()
        executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 1)

        image_paths = [os.path.join(self.path, f) for f in os.listdir(self.path) if f.endswith('.png')]
        tasks = [loop.run_in_executor(executor, self.process_image, image_path) for image_path in image_paths]
        results = await asyncio.gather(*tasks)

        for i, (premultiplied, inv_alpha) in enumerate(results):
            if not self._is_running:
                break

            self.stingerPreMultipliedImages.append(premultiplied)
            self.stingerInvAlphaImages.append(inv_alpha)
            self.progressUpdated.emit(int((i + 1) / len(image_paths) * 100))

        self.stingerReady.emit()

    @staticmethod
    def process_image(image_path):
        image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if image is None:
            logging.error(f"Failed to read image: {image_path}. It may be corrupted or unsupported.")
            image = np.random.randint(0, 255, (1080, 1920, 4), dtype=np.uint8)
        b, g, r, a = cv2.split(image)
        ia = cv2.bitwise_not(a)/255.0
        inv_alpha = cv2.merge((ia, ia, ia))
        a = a / 255.0
        alpha = cv2.merge((a, a, a))
        rgb_image = cv2.merge((b, g, r))
        premultiplied = cv2.multiply(rgb_image.astype(np.float32), alpha, dtype=cv2.CV_8U)
        return premultiplied, inv_alpha

    def stop(self):
        self._is_running = False
