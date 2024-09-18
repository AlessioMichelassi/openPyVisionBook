# Version: 2024.09.03

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor

import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class AsyncCacheLoader(QThread):
    imagesLoaded = pyqtSignal(list, list)  # Emesso quando le immagini sono state caricate
    progressUpdated = pyqtSignal(int)  # Emesso per aggiornare la barra di progresso
    operationCompleted = pyqtSignal()  # Emesso quando l'operazione è completata

    def __init__(self, premultiply_directory, inv_alpha_directory, parent=None):
        super().__init__(parent)
        self.premultiply_directory = premultiply_directory
        self.inv_alpha_directory = inv_alpha_directory
        self.premultiplied_images = []
        self.inv_alpha_images = []
        self._is_running = True

    def run(self):
        asyncio.run(self.loadImages())

    async def loadImages(self):
        loop = asyncio.get_running_loop()
        executor = ThreadPoolExecutor(max_workers=os.cpu_count() or 1)

        premultiply_files = sorted([os.path.join(self.premultiply_directory, f)
                                    for f in os.listdir(self.premultiply_directory) if f.endswith('.png')])
        inv_alpha_files = sorted([os.path.join(self.inv_alpha_directory, f)
                                  for f in os.listdir(self.inv_alpha_directory) if f.endswith('.png')])

        total_files = len(premultiply_files)
        tasks = [
            loop.run_in_executor(executor, self.load_image_pair, premultiply_files[i], inv_alpha_files[i])
            for i in range(total_files)
        ]
        results = await asyncio.gather(*tasks)

        for i, (premultiplied, inv_alpha) in enumerate(results):
            if not self._is_running:
                break

            self.premultiplied_images.append(premultiplied)
            self.inv_alpha_images.append(inv_alpha)
            self.progressUpdated.emit(int((i + 1) / total_files * 100))

        self.imagesLoaded.emit(self.premultiplied_images, self.inv_alpha_images)
        self.operationCompleted.emit()

    @staticmethod
    def load_image_pair(premultiply_path, inv_alpha_path):
        premultiplied_image = cv2.imread(premultiply_path, cv2.IMREAD_UNCHANGED)
        inv_alpha_image = cv2.imread(inv_alpha_path, cv2.IMREAD_UNCHANGED)

        if premultiplied_image is None:
            logging.error(f"Failed to read premultiplied image: {premultiply_path}.")
            premultiplied_image = np.zeros((1080, 1920, 3), dtype=np.uint8)

        if inv_alpha_image is None:
            logging.error(f"Failed to read inv alpha image: {inv_alpha_path}.")
            inv_alpha_image = np.zeros((1080, 1920, 3), dtype=np.uint8)

        return premultiplied_image, inv_alpha_image

    def stop(self):
        self._is_running = False