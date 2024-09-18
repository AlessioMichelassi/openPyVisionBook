import numpy as np
from PyQt6.QtCore import *

from cap5.mainDir.inputDevice.baseDevice.baseClass.baseClass_Extended import BaseClassExtended


class SaltAndPepperGenerator(BaseClassExtended):

    def __init__(self, resolution=QSize(1920, 1080)):
        super().__init__(resolution)
        self._name = self.__class__.__name__
        self.resolution = resolution
        self.salt_prob = 0.05
        self.pepper_prob = 0.03
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)
        self.running = True

    def captureFrame(self):
        """
        Sovrascrive la funzione captureFrame della classe base, mantenendo la funzionalità originale.
        """
        super().captureFrame()
        self._frame = self.generateNoise()

    def generateNoise(self):
        height, width = self.resolution.height(), self.resolution.width()
        # Create a blank image with all pixels set to middle gray
        image = np.ones((height, width, 3), dtype=np.uint8) * 127

        # Add salt noise (white pixels)
        num_salt = np.ceil(self.salt_prob * height * width)
        coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape[:2]]
        image[coords[0], coords[1], :] = 255

        # Add pepper noise (black pixels)
        num_pepper = np.ceil(self.pepper_prob * height * width)
        coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape[:2]]
        image[coords[0], coords[1], :] = 0

        return np.ascontiguousarray(image)

    def setSaltProbability(self, salt_prob):
        self.salt_prob = salt_prob

    def setPepperProbability(self, pepper_prob):
        self.pepper_prob = pepper_prob

    def serialize(self):
        # Chiama il metodo serialize della classe base
        base_data = super().serialize()
        base_data.update({
            'salt_prob': self.salt_prob,
            'pepper_prob': self.pepper_prob
        })
        return base_data

    def deserialize(self, data):
        # Chiama il metodo deserialize della classe base
        super().deserialize(data)
        # Estrai e imposta i dati specifici di SaltAndPepperGenerator
        self.salt_prob = data.get('salt_prob', 0.05)
        self.pepper_prob = data.get('pepper_prob', 0.03)
        self._frame = self.generateNoise()
