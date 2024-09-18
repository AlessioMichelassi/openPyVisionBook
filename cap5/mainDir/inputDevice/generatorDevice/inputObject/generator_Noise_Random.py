import numpy as np


from PyQt6.QtCore import QSize
from cap5.mainDir.inputDevice.baseDevice.baseClass.baseClass_Extended import BaseClassExtended


class RandomNoiseGenerator(BaseClassExtended):
    def __init__(self, resolution=QSize(1920, 1080)):
        super().__init__(resolution)
        self._name = self.__class__.__name__
        self.resolution = resolution
        self.running = True

    def captureFrame(self):
        """
        Generate a random noise frame.
        """
        self.updateFps()
        self._frame = np.random.randint(0, 255, (self.resolution.height(), self.resolution.width(), 3), dtype=np.uint8)

    def getFrame(self):
        return self._frame

    def serialize(self):
        # Chiama il metodo serialize della classe base
        base_data = super().serialize()
        return base_data

    def deserialize(self, data):
        # Chiama il metodo deserialize della classe base
        super().deserialize(data)
        # Estrai e imposta i dati specifici di RandomNoiseGenerator
        pass


if __name__ == "__main__":
    generator = RandomNoiseGenerator()
    print("Generator started.")
    generator.captureFrame()
    frame = generator.getFrame()
    print(f"Frame generated with mean value: {np.mean(frame)}")

