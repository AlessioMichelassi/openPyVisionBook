import logging

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class DesktopCaptureWidget(QWidget):
    typeChanged = pyqtSignal(dict)
    paramsChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.screenRegion = (0, 0, 1920, 1080)
        self.btnRefresh = QPushButton("Refresh", self)
        self.cmbScreenIndex = QComboBox(self)
        self.screenList = self.getAvailableScreens()
        self.cmbScreenIndex.addItems(self.screenList)
        self.btnConfig = QPushButton("Config", self)
        self.btnConfig.setEnabled(False)
        self.configDialog = None
        self.currentConfig = {}
        self.initUI()
        self.initConnections()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        label = QLabel("Screen Index:", self)
        main_layout.addWidget(self.btnRefresh)
        main_layout.addWidget(label)
        main_layout.addWidget(self.cmbScreenIndex)
        main_layout.addWidget(self.btnConfig)
        self.setLayout(main_layout)

    def initConnections(self):
        self.btnRefresh.clicked.connect(self.refreshScreenList)
        self.cmbScreenIndex.currentIndexChanged.connect(self.onComboChanges)
        self.btnConfig.clicked.connect(self.onConfigClicked)

    def onComboChanges(self):
        self.typeChanged.emit({
            'type': 'desktopCapture',
            'params': {
                'screenIndex': self.cmbScreenIndex.currentIndex(),
                'screenRegion': self.screenRegion
            }
        })

    def onConfigClicked(self):
        pass

    def refreshScreenList(self):
        screenText = self.cmbScreenIndex.currentText()
        self.screenList = self.getAvailableScreens()
        self.cmbScreenIndex.addItems(self.screenList)
        try:
            index = self.screenList.index(screenText)
            self.cmbScreenIndex.setCurrentIndex(index)
        except ValueError:
            logging.warning(f"Screen {screenText} is not available anymore")

    @staticmethod
    def getAvailableScreens():
        screens = QGuiApplication.screens()
        screen_names = [screen.name() for screen in screens]
        return screen_names

    def updateInputObject(self):
        # Emette un segnale di cambio parametri
        self.paramsChanged.emit({
            'screenIndex': self.cmbScreenIndex.currentIndex(),
            'screenRegion': self.screenRegion
        })

    def serialize(self):
        return {
            'screenIndex': self.cmbScreenIndex.currentIndex(),
            'params': {
                'screenIndex': self.cmbScreenIndex.currentIndex(),
                'screenCaptureSize': self.screenRegion
            }

        }

    def deserialize(self, data):
        print(f"Deserializing {data}")
        self.cmbScreenIndex.setCurrentIndex(data['screenIndex'])


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    screenCaptureWidget = DesktopCaptureWidget()
    screenCaptureWidget.paramsChanged.connect(print)
    screenCaptureWidget.typeChanged.connect(print)
    screenCaptureWidget.show()
    sys.exit(app.exec())
