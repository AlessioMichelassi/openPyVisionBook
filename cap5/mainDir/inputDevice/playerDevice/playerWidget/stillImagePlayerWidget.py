from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class StillImagePlayerWidget(QWidget):
    typeChange = pyqtSignal(dict)
    paramsChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.btnLoadImage = QPushButton("Load Image", self)
        self.lneImagePath = QLineEdit("", self)
        self.btnConfig = QPushButton("Config", self)
        self.btnConfig.setEnabled(False)
        self.configDialog = None
        self.currentConfig = {}

        self.initUI()
        self.initConnections()

    def initUI(self):
        """
        Sets up the UI layout.
        """
        main_layout = QHBoxLayout(self)
        label = QLabel("Image Path:", self)
        main_layout.addWidget(label)
        main_layout.addWidget(self.lneImagePath)
        main_layout.addWidget(self.btnLoadImage)
        main_layout.addWidget(self.btnConfig)

        self.setLayout(main_layout)

    def initConnections(self):
        """
        Connects the buttons to their respective handlers.
        """
        self.btnLoadImage.clicked.connect(self.onLoadImage)
        self.btnConfig.clicked.connect(self.onConfig)

    def onLoadImage(self):
        """
        Opens a file generatorDialog to load an image. Updates the input object and enables the config button.
        """
        fileDialog = QFileDialog(self)
        fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        fileDialog.setNameFilter("Images (*.png *.jpg *.bmp)")

        if fileDialog.exec():
            imagePath = fileDialog.selectedFiles()[0]
            self.lneImagePath.setText(imagePath)
            # Enable the config button only if an image is loaded
            self.btnConfig.setEnabled(True)
            self.paramsChanged.emit({'imagePath': imagePath})
        else:
            # Disable the config button if no image is loaded
            self.btnConfig.setEnabled(False)

    def onConfig(self):
        """
        Opens the configuration generatorDialog for the selected image type.
        """
        """self.configDialog = ImagePlayerConfigDialog(self.currentConfig)
        returnOk = self.configDialog.exec()
        if returnOk:
            config = self.configDialog.getConfiguration()
            self.currentConfig = config
            self.paramsChanged.emit(config)"""
        pass

    def serialize(self):
        """
        Serializes the current state of the widget into a dictionary.
        """
        return {
            'type': "Still Image Player",
            'imagePath': self.lneImagePath.text(),
        }

    def deserialize(self, data):
        """
        Deserializes the widget state from a dictionary and updates the UI.
        """
        self.lneImagePath.setText(data['imagePath'])


if __name__ == "__main__":
    import sys
    from cap5.mainDir.inputDevice.playerDevice.inputObject.player_StillImage import StillImagePlayer

    app = QApplication(sys.argv)
    inputDevice = StillImagePlayer("Still Image Player")
    stillImagePlayerWidget = StillImagePlayerWidget()
    stillImagePlayerWidget.show()
    sys.exit(app.exec())
