from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import *

from cap5.cap5_3.videoHub.inputDevice.generatorDevice.generatorWidget.baseInputWidget import BaseInputWidget


class SmpteGeneratorWidget(BaseInputWidget):
    """
        An InputDevice for managing the SMPTE generator.
        It brings together the thread, the input object, and the graphical interface,
        acting as the interface for the mixer.
        """
    paramsChanged = pyqtSignal(dict)

    def __init__(self, _inputDevice, parent=None):
        super().__init__(_inputDevice, parent=parent)
        self.inputDevice = _inputDevice
        self.cmbSmpteType = QComboBox(self)
        self.smpteTypeList = ["Smpte"]
        self.cmbSmpteType.addItems(self.smpteTypeList)

        self.initUI()
        self.initConnections()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        label = QLabel("Smpte Type:", self)
        main_layout.addWidget(label)
        main_layout.addWidget(self.cmbSmpteType)
        self.setLayout(main_layout)

    def initConnections(self):
        self.cmbSmpteType.currentIndexChanged.connect(self.onComboChanges)

    def onComboChanges(self):
        smpteType = self.cmbSmpteType.currentText()
        print(f"Noise type changed to {smpteType}")
        self.paramsChanged.emit({'smpteType': smpteType})

    def serialize(self):
        return {
            'smpteType': self.cmbSmpteType.currentText(),
        }

    def deserialize(self, data):
        self.cmbSmpteType.setCurrentText(data['noiseType'])
