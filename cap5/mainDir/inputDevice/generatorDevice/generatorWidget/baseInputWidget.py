from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


class BaseInputWidget(QWidget):
    name = "default"
    inputDevice = None

    def __init__(self, _inputDevice, resolution=QSize(1920,1080), parent=None):
        super().__init__(parent)
        self.inputDevice = _inputDevice
        self._resolution = resolution
        self.inputParameters = {}



