from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox, QDoubleSpinBox


class BaseConfigurationDialog(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.config = {}  # Dizionario per memorizzare le configurazioni
        self.main_Layout = QVBoxLayout(self)
        self.applyButton = QPushButton("Apply", self)
        self.cancelButton = QPushButton("Cancel", self)
        self.initUI()
        self.initConnections()

    def initUI(self):
        """Inizializza l'interfaccia utente comune."""
        # Layout per i pulsanti Apply e Cancel
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.applyButton)
        buttonLayout.addWidget(self.cancelButton)

        self.main_Layout.addLayout(buttonLayout)
        self.setLayout(self.main_Layout)

    def initConnections(self):
        self.applyButton.clicked.connect(self.accept)
        self.cancelButton.clicked.connect(self.reject)
        self.accepted.connect(self.applySettings)

    def setConfiguration(self, config):
        """Metodo per impostare la configurazione iniziale."""
        self.config = config

    def getConfiguration(self):
        """Metodo per ottenere la configurazione attuale."""
        return self.config

    def applySettings(self):
        """Applica le impostazioni attuali."""
        pass  # Implementato nelle sottoclassi se necessario

    def createSpinBox(self, label, min_value, max_value, default_value, config_key):
        """Metodo di utilità per creare un QSpinBox con etichetta."""
        lbl = QLabel(label, self)
        self.main_Layout.insertWidget(self.main_Layout.count() - 1, lbl)
        spinBox = QSpinBox(self)
        spinBox.setRange(min_value, max_value)
        spinBox.setValue(default_value)
        self.main_Layout.insertWidget(self.main_Layout.count() - 1, spinBox)
        # Associa il valore al dizionario config
        spinBox.valueChanged.connect(lambda val: self.config.update({config_key: val}))
        return spinBox

    def createDoubleSpinBox(self, label, min_value, max_value, default_value, config_key):
        """Metodo di utilità per creare un QDoubleSpinBox con etichetta."""
        lbl = QLabel(label, self)
        self.main_Layout.insertWidget(self.main_Layout.count() - 1, lbl)
        doubleSpinBox = QDoubleSpinBox(self)
        doubleSpinBox.setRange(min_value, max_value)
        doubleSpinBox.setSingleStep(0.01)
        doubleSpinBox.setValue(default_value)
        self.main_Layout.insertWidget(self.main_Layout.count() - 1, doubleSpinBox)
        # Associa il valore al dizionario config
        doubleSpinBox.valueChanged.connect(lambda val: self.config.update({config_key: val}))
        return doubleSpinBox
