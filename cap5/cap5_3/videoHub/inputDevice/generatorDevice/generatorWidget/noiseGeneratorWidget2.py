from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from cap5.cap5_3.videoHub.inputDevice.generatorDevice.generatorWidget.generatorDialog.noiseConfigDialog import \
    RandomNoiseConfigDialog, SaltAndPepperConfigDialog, GrainConfigDialog


class NoiseGeneratorWidget2(QWidget):
    typeChange = pyqtSignal(dict)
    paramsChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.noiseTypeList = ["Random", "Salt and Pepper", "Grain"]
        self.cmNoiseType = QComboBox(self)
        self.btnConfig = QPushButton("Config", self)
        self.configDialog = None
        self.currentConfig = {}
        self.initUI()
        self.initConnections()

    def initUI(self):
        self.cmNoiseType.addItems(self.noiseTypeList)
        main_layout = QHBoxLayout(self)
        label = QLabel("Noise Type:", self)
        main_layout.addWidget(label)
        main_layout.addWidget(self.cmNoiseType)
        main_layout.addWidget(self.btnConfig)
        self.setLayout(main_layout)

    def initConnections(self):
        self.cmNoiseType.currentIndexChanged.connect(self.onComboChanges)
        self.btnConfig.clicked.connect(self.onConfigClicked)

    def onComboChanges(self, index):
        noiseType = self.cmNoiseType.currentText()
        print(f"Noise type changed to {noiseType}")
        self.typeChange.emit({'noiseType': noiseType})

    def onConfigClicked(self):
        noiseType = self.cmNoiseType.currentText()
        if noiseType == "Random":
            self.configDialog = RandomNoiseConfigDialog()
        elif noiseType == "Salt and Pepper":
            self.configDialog = SaltAndPepperConfigDialog()
        elif noiseType == "Grain":
            self.configDialog = GrainConfigDialog()
        else:
            return

        # Preimposta la configurazione corrente nel dialogo
        if noiseType in self.currentConfig:
            self.configDialog.setConfiguration(self.currentConfig[noiseType])

        returnOk = self.configDialog.exec()
        if returnOk:
            config = self.configDialog.getConfiguration()
            self.currentConfig[noiseType] = config  # Salva la configurazione corrente
            configDictionary = {'noiseType': noiseType}
            configDictionary.update(config)
            self.paramsChanged.emit(configDictionary)

    def serialize(self):
        noiseType = self.cmNoiseType.currentText()
        data = {
            'noiseType': noiseType,
        }
        if noiseType in self.currentConfig:
            data['params'] = self.currentConfig[noiseType]
        return data

    def deserialize(self, data):
        noiseType = data.get('noiseType', 'Random')
        index = self.noiseTypeList.index(noiseType) if noiseType in self.noiseTypeList else 0
        self.cmNoiseType.setCurrentIndex(index)
        self.currentConfig[noiseType] = data.get('params', {})


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    widget = NoiseGeneratorWidget2()

    widget.show()
    sys.exit(app.exec())
