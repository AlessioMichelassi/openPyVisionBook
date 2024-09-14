import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from cap5.mainDir.inputs.baseClass.baseClass_Extended import BaseClassExtended


class StillImagePlayer(BaseClassExtended):

    def __init__(self, imagePath, resolution=QSize(1920, 1080)):
        super().__init__(resolution)
        self._name = self.__class__.__name__
        self.resolution = resolution
        self.imagePath = imagePath
        if imagePath:
            self.loadImage(imagePath)
        self.running = False

    def loadImage(self, imagePath):
        try:
            image = cv2.imread(imagePath, cv2.IMREAD_COLOR)
            if image is None:
                print(f"Error loading image: {imagePath}")
            # se le dimensioni dell'immagine sono diverse da quelle
            # specificate, ridimensiona l'immagine
            if image.shape[:2] != (self.resolution.height(), self.resolution.width()):
                image = cv2.resize(image, (self.resolution.width(), self.resolution.height()))
            self._frame = image
        except Exception as e:
            print(f"Error loading image: {e}")
            self._frame = np.zeros((self.resolution.height(),
                                    self.resolution.width(), 3), dtype=np.uint8)

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

    def serialize(self):
        """
        Sovrascrive la funzione serialize della classe base, mantenendo la funzionalità originale.
        """
        base_data = super().serialize()
        base_data.update({
            'path': self.imagePath
        })
        return base_data

    def deserialize(self, data):
        """
        Sovrascrive la funzione deserialize della classe base, mantenendo la funzionalità originale.
        """
        super().deserialize(data)
        self.loadImage(data.get('path', ''))
        self.imagePath = data.get('path', '')
