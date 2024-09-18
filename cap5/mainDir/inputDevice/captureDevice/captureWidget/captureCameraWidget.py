from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from cap5.mainDir.inputDevice.captureDevice.inputObject.deviceFinder.DeviceUpdaterWidget import DeviceUpdaterWidget


class CameraCaptureWidget(QWidget):
    typeChanged = pyqtSignal(dict)
    paramsChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cmbCameraType = DeviceUpdaterWidget(self)
        self.cmbSpecializedCapture = QComboBox(self)
        self.cameraTypeList = ["videoCapture", "oldUsbCamera"]
        self.cmbSpecializedCapture.addItems(self.cameraTypeList)
        self.cmbSpecializedCapture.setCurrentIndex(0)
        self.cameraIndex = 0
        self.deviceName = ""
        self.initUI()
        self.initConnections()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        label = QLabel("Input Type:", self)
        main_layout.addWidget(label)
        main_layout.addWidget(self.cmbCameraType)
        lblSpecializedCapture = QLabel("Specialized Capture:", self)
        main_layout.addWidget(lblSpecializedCapture)
        main_layout.addWidget(self.cmbSpecializedCapture)
        self.setLayout(main_layout)

    def initConnections(self):
        self.cmbCameraType.deviceChanged.connect(self.onComboChanges)
        self.cmbSpecializedCapture.currentIndexChanged.connect(self.onParamsChanged)

    def onComboChanges(self, _dict):
        self.typeChanged.emit({
            'type': 'cameraCapture',
            'params': {
                'cameraIndex': _dict["deviceIndex"],
            }})
        print(f"CameraCaptureWidget - onComboChanges: {_dict}")

    def onParamsChanged(self):
        pass

    def serialize(self):
        return {
            'type': 'cameraCapture',
            'params': {
                'deviceIndex': self.cmbCameraType.currentIndex(),
            }
        }


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    cameraCaptureWidget = CameraCaptureWidget()
    cameraCaptureWidget.typeChanged.connect(print)
    cameraCaptureWidget.show()
    sys.exit(app.exec())
