# Version: 2024.09.03

import os
import json
import time
import cv2
import numpy as np
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from mainDir.inputs.player.player_StingerMixBus import StingerForMixBusPlayer
# Assumendo che OpenGLViewer sia una classe definita in un altro modulo
from mainDir.output.openGLViewer import OpenGLViewer

# Configurazione del logger


from mainDir.videoHub.systemWidget.stingerLoaderWidget import StingerLoaderWidget

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class VideoAppForStinger(QWidget):
    def __init__(self, input_object):
        super().__init__()
        self.inputObject = input_object
        self.index = 0

        # UI Elements
        self.viewer1 = OpenGLViewer()
        self.viewer2 = OpenGLViewer()
        self.viewer1.setFixedSize(640, 360)
        self.viewer2.setFixedSize(640, 360)
        self.fpsLabel = QLabel("FPS: 0.00")
        self.displayLabel = QLabel()

        # Timer for updating frames
        self.uiTimer = QTimer(self)
        self.uiTimer.timeout.connect(self.display_frame)
        self.uiTimer.start(1000 // 60)  # ~60 FPS

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.viewer1)
        layout.addWidget(self.viewer2)
        layout.addWidget(self.fpsLabel)
        layout.addWidget(self.displayLabel)
        self.setLayout(layout)

    def display_frame(self):
        try:
            if self.index < len(self.inputObject.stingerPreMultipliedImages):
                frame1 = self.inputObject.stingerPreMultipliedImages[self.index]
                frame2 = self.inputObject.stingerInvAlphaImages[self.index]

                if frame1 is not None and frame2 is not None:
                    self.viewer1.setFrame(frame1)
                    self.viewer2.setFrame(frame2)
                    self.index += 1
                else:
                    logging.error("Frame is None. Resetting index.")
                    self.index = 0
            else:
                # Non loggare più l'avviso "Index out of range", ma semplicemente resettare l'indice
                self.index = 0
        except Exception as e:
            logging.error(f"Error in display_frame: {e}")
            self.index = 0

    def closeEvent(self, event):
        self.uiTimer.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    loader = StingerLoaderWidget()
    loader.show()

    video_app = None


    def onStingerReady(stinger):
        global video_app
        logging.info("Stinger is ready!")
        video_app = VideoAppForStinger(stinger)
        video_app.show()


    loader.stingerReady.connect(onStingerReady)

    try:
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Application error: {e}")
