from PyQt6.QtWidgets import *

from mainDir.inputs.player.player_StillImage import StillImagePlayer
from mainDir.videoHub.inputWidget.baseInputWidget import BaseInputWidget
from mainDir.widgets.imageEditor.pixelSmith import PixelSmith200


class StillImagePlayerWidget(BaseInputWidget):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.btnLoadImage = QPushButton("Load Image", self)
        self.lneImagePath = QLineEdit("", self)
        self.type = "StillLoader"
        self.btnConfig = QPushButton("Config", self)
        self.initUI()
        self.initConnections()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        label = QLabel("Image Path:", self)
        main_layout.addWidget(label)
        main_layout.addWidget(self.btnConfig)
        main_layout.addWidget(self.lneImagePath)
        main_layout.addWidget(self.btnLoadImage)

        self.setLayout(main_layout)

    def initConnections(self):
        self.btnLoadImage.clicked.connect(self.onLoadImage)
        self.btnConfig.clicked.connect(self.onConfig)

    def onLoadImage(self):
        fileDialog = QFileDialog(self)
        fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        fileDialog.setNameFilter("Images (*.png *.jpg *.bmp)")

        if fileDialog.exec():
            self.lneImagePath.setText(fileDialog.selectedFiles()[0])
            self.updateInputObject()
            # Abilita il pulsante Config solo se l'immagine è stata caricata
            self.btnConfig.setEnabled(True)
        else:
            # Disabilita il pulsante Config se l'immagine non è stata caricata
            self.btnConfig.setEnabled(False)

    def updateInputObject(self):
        self.inputObject = StillImagePlayer(self.lneImagePath.text())
        self.parametersChanged.emit(self.serialize())
        # Aggiorna la disponibilità del pulsante Config basato sulla validità dell'immagine caricata
        self.btnConfig.setEnabled(self.inputObject is not None and self.inputObject.getFrame() is not None)

    def onConfig(self):
        """Apre PixelSmith200 per la configurazione dell'immagine."""
        if self.inputObject and self.inputObject.getFrame() is not None:
            pixelSmithDialog = PixelSmith200(self.lneImagePath.text(), parent=self)
            if pixelSmithDialog.exec() == QDialog.DialogCode.Accepted:
                # Dopo che l'utente ha finito di modificare l'immagine, aggiorna l'inputObject se necessario
                self.updateInputObject()

    def getInput(self):
        return self.inputObject

    def applyConfiguration(self, config):
        self.lneImagePath.setText(config.get('image_path', ''))
        self.updateInputObject()

    def serialize(self):
        return {
            'name': self.getName(),
            'type': self.type,
            'imagePath': self.lneImagePath.text(),
        }

    def deserialize(self, data):
        self.setName(data['name'])
        self.lneImagePath.setText(data['imagePath'])
        self.updateInputObject()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    stillImagePlayerWidget = StillImagePlayerWidget()
    stillImagePlayerWidget.show()
    sys.exit(app.exec())
