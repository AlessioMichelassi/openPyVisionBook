import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from mainDir.inputs.baseClass.baseClass_Extended import BaseClassExtended


class StingerForMixBusPlayer(BaseClassExtended):

    def __init__(self, imagePath, position, resolution=QSize(1920, 1080)):
        super().__init__(resolution)
        self._name = self.__class__.__name__
        self.resolution = resolution
        self.stingerPosition = position
        self.index = 0
        self.isCached = False
        self.stingerPath = imagePath
        self.stingerInvAlphaImagesPath = ""
        self.stingerPreMultipliedImagesPath = ""
        self.stingerPreMultipliedImages = []
        self.stingerInvAlphaImages = []

    def setStingerPremultipliedImages(self, images: list):
        self.stingerPreMultipliedImages = images

    def setStingerInvAlphaImages(self, images: list):
        self.stingerInvAlphaImages = images

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
            'isCached': self.isCached,
            'stingerFolder': self.stingerPath,
            'stingerInvAlphaImagesPath': self.stingerInvAlphaImagesPath,
            'stingerPreMultipliedImagesPath': self.stingerPreMultipliedImagesPath
        })
        return base_data

    def deserialize(self, data):
        """
        Sovrascrive la funzione deserialize della classe base, mantenendo la funzionalità originale.
        """
        super().deserialize(data)
        self.isCached = data['isCached']
        if self.isCached:
            self.stingerInvAlphaImagesPath = data['stingerInvAlphaImagesPath']
            self.stingerPreMultipliedImagesPath = data['stingerPreMultipliedImagesPath']
