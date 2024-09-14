from PyQt6.QtWidgets import *

from cap5.cap5_3.videoHub.inputDevice.generatorDevice.generatorWidget.generatorDialog.baseConfigurationDialog import \
    BaseConfigurationDialog


class RandomNoiseConfigDialog(BaseConfigurationDialog):
    def __init__(self, parent=None):
        super().__init__("Random Noise Configuration", parent)
        self.initUI()
        # Nessuna configurazione specifica per Random Noise

    def initUI(self):
        label = QLabel("Random Noise Generator does not have configurable parameters.", self)
        self.main_Layout.insertWidget(0, label)  # Inserisce l'etichetta all'inizio
        super().initUI()  # Richiama l'inizializzazione comune

    def applySettings(self):
        # Nessuna configurazione da applicare
        super().applySettings()


class SaltAndPepperConfigDialog(BaseConfigurationDialog):
    saltSpinBox: QDoubleSpinBox
    pepperSpinBox: QDoubleSpinBox

    def __init__(self, parent=None):
        super().__init__("Salt and Pepper Noise Configuration", parent)

    def initUI(self):
        default_salt_prob = 0.1
        default_pepper_prob = 0.1
        self.saltSpinBox = self.createDoubleSpinBox(
            "Salt Probability:", 0.0, 1.0, default_salt_prob, "salt_prob"
        )
        self.pepperSpinBox = self.createDoubleSpinBox(
            "Pepper Probability:", 0.0, 1.0, default_pepper_prob, "pepper_prob"
        )
        super().initUI()  # Richiama l'inizializzazione comune

    def setConfiguration(self, config):
        super().setConfiguration(config)
        self.saltSpinBox.setValue(self.config.get('salt_prob', 0.1))
        self.pepperSpinBox.setValue(self.config.get('pepper_prob', 0.1))

    def applySettings(self):
        # I valori sono già aggiornati in self.config tramite le connessioni dei spin box
        super().applySettings()


class GrainConfigDialog(BaseConfigurationDialog):
    grainSizeSpinBox: QSpinBox
    rSpeedSpinBox: QSpinBox
    gSpeedSpinBox: QSpinBox
    bSpeedSpinBox: QSpinBox
    rOffsetSpinBox: QSpinBox
    gOffsetSpinBox: QSpinBox
    bOffsetSpinBox: QSpinBox

    def __init__(self, parent=None):
        super().__init__("Grain Noise Configuration", parent)

    def initUI(self):
        # Valori di default
        default_values = {
            'grain_size': 3,
            'r_speed': 2,
            'g_speed': 1,
            'b_speed': 3,
            'r_offset': 2,
            'g_offset': 0,
            'b_offset': 4
        }
        self.grainSizeSpinBox = self.createSpinBox(
            "Grain Size:", 1, 10, default_values['grain_size'], "grain_size"
        )
        self.rSpeedSpinBox = self.createSpinBox(
            "Red Speed:", 0, 10, default_values['r_speed'], "r_speed"
        )
        self.gSpeedSpinBox = self.createSpinBox(
            "Green Speed:", 0, 10, default_values['g_speed'], "g_speed"
        )
        self.bSpeedSpinBox = self.createSpinBox(
            "Blue Speed:", 0, 10, default_values['b_speed'], "b_speed"
        )
        self.rOffsetSpinBox = self.createSpinBox(
            "Red Offset:", 0, 100, default_values['r_offset'], "r_offset"
        )
        self.gOffsetSpinBox = self.createSpinBox(
            "Green Offset:", 0, 100, default_values['g_offset'], "g_offset"
        )
        self.bOffsetSpinBox = self.createSpinBox(
            "Blue Offset:", 0, 100, default_values['b_offset'], "b_offset"
        )
        super().initUI()  # Richiama l'inizializzazione comune

    def setConfiguration(self, config):
        super().setConfiguration(config)
        self.grainSizeSpinBox.setValue(self.config.get('grain_size', 3))
        self.rSpeedSpinBox.setValue(self.config.get('r_speed', 2))
        self.gSpeedSpinBox.setValue(self.config.get('g_speed', 1))
        self.bSpeedSpinBox.setValue(self.config.get('b_speed', 3))
        self.rOffsetSpinBox.setValue(self.config.get('r_offset', 2))
        self.gOffsetSpinBox.setValue(self.config.get('g_offset', 0))
        self.bOffsetSpinBox.setValue(self.config.get('b_offset', 4))

    def applySettings(self):
        # I valori sono già aggiornati in self.config tramite le connessioni dei spin box
        super().applySettings()

