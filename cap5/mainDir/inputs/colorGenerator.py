import numpy as np
from PyQt6.QtCore import *

from cap5.mainDir.inputs.baseClass_Extended import BaseClassExtended


class ColorGenerator(BaseClassExtended):

    def __init__(self, synchObject, resolution=QSize(1920, 1080)):
        super().__init__(synchObject, resolution)
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        color = np.random.randint(0, 255, 3)
        self.generateColor(color)

    def generateColor(self, color):
        self._frame[:, :] = color

    def captureFrame(self):
        """
        Sovrascrive la funzione captureFrame della classe base, mantenendo la funzionalità originale.
        """
        super().captureFrame()

    def getFrame(self):
        """
        Sovrascrive la funzione getFrame della classe base, mantenendo la funzionalità originale.
        """
        return super().getFrame()
