import numpy as np
from PyQt6.QtCore import *

from cap5.mainDir.inputDevice.baseDevice.baseClass.baseClass_Extended import BaseClassExtended


class GrainGenerator(BaseClassExtended):

    def __init__(self, resolution=QSize(1920, 1080)):
        super().__init__(resolution)
        self._name = self.__class__.__name__
        self.resolution = resolution
        self._grain_size = 3
        self._r_speed = 2
        self._g_speed = 1
        self._b_speed = 3
        self._r_offset = 2
        self._g_offset = 0
        self._b_offset = 4
        self._frame = np.zeros((resolution.height(), resolution.width(), 3), dtype=np.uint8)

    def captureFrame(self):
        """
        Sovrascrive la funzione captureFrame della classe base, mantenendo la funzionalità originale.
        """
        super().captureFrame()
        self._frame = self.generate_noise()

    def generate_noise(self):
        height, width = self.resolution.height(), self.resolution.width()
        grain_shape = (height // self._grain_size, width // self._grain_size)

        r_noise = np.random.randint(10, 200, grain_shape, dtype=np.uint8)
        g_noise = np.random.randint(10, 200, grain_shape, dtype=np.uint8)
        b_noise = np.random.randint(10, 200, grain_shape, dtype=np.uint8)

        r_noise = np.kron(r_noise, np.ones((self._grain_size, self._grain_size), dtype=np.uint8))
        g_noise = np.kron(g_noise, np.ones((self._grain_size, self._grain_size), dtype=np.uint8))
        b_noise = np.kron(b_noise, np.ones((self._grain_size, self._grain_size), dtype=np.uint8))

        r_noise = np.roll(r_noise, self._r_offset, axis=1)
        g_noise = np.roll(g_noise, self._g_offset, axis=0)
        b_noise = np.roll(b_noise, self._b_offset, axis=0)
        self._r_offset = (self._r_offset + self._r_speed) % width
        self._g_offset = (self._g_offset + self._g_speed) % height
        self._b_offset = (self._b_offset + self._b_speed) % height
        return np.dstack((b_noise, g_noise, r_noise))

    def setGrainSize(self, grain_size):
        self._grain_size = grain_size

    def setRSpeed(self, r_speed):
        self._r_speed = r_speed

    def setGSpeed(self, g_speed):
        self._g_speed = g_speed

    def setBSpeed(self, b_speed):
        self._b_speed = b_speed

    def setROffset(self, r_offset):
        self._r_offset = r_offset

    def setGOffset(self, g_offset):
        self._g_offset = g_offset

    def setBOffset(self, b_offset):
        self._b_offset = b_offset

    def serialize(self):
        # Chiama il metodo serialize della classe base
        base_data = super().serialize()
        base_data.update({
            'grain_size': self._grain_size,
            'r_speed': self._r_speed,
            'g_speed': self._g_speed,
            'b_speed': self._b_speed,
            'r_offset': self._r_offset,
            'g_offset': self._g_offset,
            'b_offset': self._b_offset
        })
        return base_data

    def deserialize(self, data):
        super().deserialize(data)
        # Estrai e imposta i dati specifici di GrainGenerator
        self._grain_size = data.get('grain_size', 3)
        self._r_speed = data.get('r_speed', 2)
        self._g_speed = data.get('g_speed', 1)
        self._b_speed = data.get('b_speed', 3)
        self._r_offset = data.get('r_offset', 2)
        self._g_offset = data.get('g_offset', 0)
        self._b_offset = data.get('b_offset', 4)
        self._frame = self.generate_noise()