from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from cap5.cap5_3.videoHub.inputDevice.generatorDevice.generatorWidget.generatorDialog.baseConfigurationDialog import BaseConfigurationDialog


class ImagePlayerConfigDialog(BaseConfigurationDialog):
    def __init__(self, current_config=None, parent=None):
        super().__init__("Image Player Configuration", parent)
        self.current_config = current_config if current_config else {}
        self.scale_mode = self.current_config.get('scale_mode', 'Fit')

        self.graphicsView = QGraphicsView(self)
        self.graphicsScene = QGraphicsScene(self)
        self.graphicsView.setScene(self.graphicsScene)

        self.image_item = None  # Questo sarà il nostro ResizableGraphicsItem

        self.initUI()
        self.initConnections()

    def initUI(self):
        """Inizializza l'interfaccia utente specifica per Image Player."""
        super().initUI()

        # Inserisci la vista grafica
        self.main_Layout.insertWidget(0, self.graphicsView)

        # Opzioni di scalatura
        self.scaleComboBox = QComboBox(self)
        self.scaleComboBox.addItems(["Fit", "Stretch", "Keep Aspect Ratio by Width", "Keep Aspect Ratio by Height"])
        self.scaleComboBox.setCurrentText(self.scale_mode)
        self.main_Layout.insertWidget(1, QLabel("Scale Mode:", self))
        self.main_Layout.insertWidget(2, self.scaleComboBox)

        # Controlli di zoom
        self.zoomSpinBox = self.createSpinBox("Zoom:", 1, 400, 100)
        self.zoomSpinBox.valueChanged.connect(self.applyZoom)

    def initConnections(self):
        """Inizializza le connessioni dei segnali specifici."""
        super().initConnections()
        self.scaleComboBox.currentTextChanged.connect(self.updateScaleMode)

    def loadImageFromNumpy(self, image_frame):
        """Carica un'immagine da un array numpy e utilizza ResizableGraphicsItem per la manipolazione."""
        if image_frame is not None:
            height, width, channel = image_frame.shape
            bytesPerLine = 3 * width
            qImg = QImage(image_frame.data, width, height, bytesPerLine, QImage.Format.Format_BGR888)
            pixmap = QPixmap.fromImage(qImg)

            # Se c'è già un'immagine nella scena, la rimuoviamo prima di aggiungerne una nuova
            if self.image_item:
                self.graphicsScene.removeItem(self.image_item)

            self.image_item = ResizableGraphicsItem(pixmap)
            self.graphicsScene.addItem(self.image_item)
            self.applyZoom()
        else:
            print("Unable to load image from numpy array: Frame is None")

    def applyZoom(self):
        """Applica lo zoom sull'immagine."""
        zoom_factor = self.zoomSpinBox.value() / 100.0
        self.graphicsView.resetTransform()
        self.graphicsView.scale(zoom_factor, zoom_factor)

    def updateScaleMode(self, scale_mode):
        """Aggiorna la modalità di scalatura dell'immagine."""
        self.scale_mode = scale_mode
        # Potresti voler implementare logiche specifiche di scalatura qui

    def applySettings(self):
        """Applica le impostazioni specifiche di Image Player."""
        super().applySettings()

    def getConfiguration(self):
        """Ottiene la configurazione corrente."""
        return {
            'scale_mode': self.scaleComboBox.currentText(),
        }

    def setConfiguration(self, config):
        """Imposta la configurazione corrente."""
        self.scaleComboBox.setCurrentText(config.get('scale_mode', 'Fit'))
        # Configurazioni aggiuntive possono essere impostate qui


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    dialog = ImagePlayerConfigDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        print(dialog.getConfiguration())
    sys.exit(app.exec())
