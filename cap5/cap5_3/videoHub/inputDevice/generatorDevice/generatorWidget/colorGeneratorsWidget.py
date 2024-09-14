from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class ColorGeneratorWidget(QWidget):
    paramsChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cmColorType = QComboBox(self)
        self.colorTypeList = ["rgb", "random", "black"]
        self.cmColorType.addItems(self.colorTypeList)

        # Aggiungiamo input fields per RGB
        self.lneColorRed = QLineEdit("0", self)
        self.lneColorGreen = QLineEdit("0", self)
        self.lneColorBlue = QLineEdit("0", self)

        # Limiti ai valori (0-255) per i colori RGB
        self.lneColorRed.setValidator(QDoubleValidator(0, 255, 0, self))
        self.lneColorGreen.setValidator(QDoubleValidator(0, 255, 0, self))
        self.lneColorBlue.setValidator(QDoubleValidator(0, 255, 0, self))

        self.initUI()
        self.initConnections()
        self.updateInputObject()

    def initUI(self):
        main_layout = QHBoxLayout(self)
        label = QLabel("Type:", self)
        main_layout.addWidget(label)
        main_layout.addWidget(self.cmColorType)

        lblRed = QLabel("Red:", self)
        main_layout.addWidget(lblRed)
        main_layout.addWidget(self.lneColorRed)

        lblGreen = QLabel("Green:", self)
        main_layout.addWidget(lblGreen)
        main_layout.addWidget(self.lneColorGreen)

        lblBlue = QLabel("Blue:", self)
        main_layout.addWidget(lblBlue)
        main_layout.addWidget(self.lneColorBlue)

        self.setLayout(main_layout)

    def initConnections(self):
        self.cmColorType.currentIndexChanged.connect(self.onComboChanges)
        self.lneColorBlue.returnPressed.connect(self.updateInputObject)
        self.lneColorGreen.returnPressed.connect(self.updateInputObject)
        self.lneColorRed.returnPressed.connect(self.updateInputObject)

    def onComboChanges(self):
        # Abilita o disabilita i campi RGB in base al tipo di colore selezionato
        if self.cmColorType.currentText() == "rgb":
            self.lneColorRed.setEnabled(True)
            self.lneColorGreen.setEnabled(True)
            self.lneColorBlue.setEnabled(True)
        else:
            self.lneColorRed.setEnabled(False)
            self.lneColorGreen.setEnabled(False)
            self.lneColorBlue.setEnabled(False)

        self.updateInputObject()

    def updateInputObject(self):
        """
        Aggiorna l'oggetto input in base alla scelta fatta nella UI.
        """
        colorType = self.cmColorType.currentText()
        # Emette un segnale di cambio parametri
        self.paramsChanged.emit(self.serialize())


    def serialize(self):
        """
        Serializza lo stato corrente dell'interfaccia grafica e dell'oggetto input.
        """
        return {
            'colorType': self.cmColorType.currentText(),
            'red': self.lneColorRed.text(),
            'green': self.lneColorGreen.text(),
            'blue': self.lneColorBlue.text(),
        }

    def deserialize(self, data):
        """
        Deserializza lo stato e aggiorna l'interfaccia grafica.
        """

        self.cmColorType.setCurrentText(data['colorType'])

        if data['colorType'] == "rgb":
            self.lneColorRed.setText(data['red'])
            self.lneColorGreen.setText(data['green'])
            self.lneColorBlue.setText(data['blue'])
        elif data['colorType'] == "random":
            self.cmColorType.setCurrentIndex(1)
        elif data['colorType'] == "black":
            self.cmColorType.setCurrentIndex(2)

        # Aggiorna l'oggetto input in base ai dati deserializzati
        self.updateInputObject()


if __name__ == "__main__":
    import sys
    from cap5.cap5_3.videoHub.inputDevice.generatorDevice.inputDevice_colorGenerator import InputDevice_ColorGenerator

    app = QApplication(sys.argv)
    inputDevice = InputDevice_ColorGenerator("ColorGenerator")
    colorGenerator = ColorGeneratorWidget(inputDevice)
    colorGenerator.paramsChanged.connect(print)
    colorGenerator.show()
    sys.exit(app.exec())
