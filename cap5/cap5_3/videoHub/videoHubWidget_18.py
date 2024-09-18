import logging
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from cap5.mainDir.inputDevice.captureDevice.inputDevice_cameraCapture import InputDevice_CameraCapture
from cap5.mainDir.inputDevice.generatorDevice.inputDevice_colorGenerator import InputDevice_ColorGenerator
from cap5.mainDir.inputDevice.generatorDevice.inputDevice_noiseGenerator import InputDevice_NoiseGenerator
from cap5.mainDir.inputDevice.generatorDevice.inputDevice_smpteGenerator import InputDevice_SmpteGenerator
from cap5.mainDir.inputDevice.captureDevice.inputDevice_desktopCapture import InputDevice_DesktopCapture
from cap5.mainDir.inputDevice.playerDevice.inputDevice_stillImagePlayerGenerator import \
    InputDevice_StillImagePlayer
from cap5.cap5_3.videoHub.videoHubData018 import VideoHubData018

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),  # Log su un file chiamato app.log
        logging.StreamHandler()  # Log su console
    ]
)


class VideoHubWidget018(QWidget):
    def __init__(self, _videoHubData, parent=None):
        super().__init__(parent)
        self.videoHubData = _videoHubData
        self.current_index = 0
        self.generator_list = [
            "Select input",
            "cameraCapture",
            "desktopCapture",
            "stillImage",
            "colorGenerator",
            "noiseGenerator",
            "smpteBarsGenerator",
        ]
        self.combo_boxes = []
        self.stacked_widgets = []
        self.active_checkboxes = []

        self.mainLayout = QVBoxLayout(self)
        self.tabWidget = QTabWidget(self)
        self.initTabs()
        self.initUI()
        self.initConnections()

    def initTabs(self):
        # Tab 1: Inputs 1-4
        tab1 = QWidget()
        tab1.setLayout(self.returnGridLayout(start=1, end=4))
        self.tabWidget.addTab(tab1, "Inputs 1-4")

        # Tab 2: Inputs 5-8
        tab2 = QWidget()
        tab2.setLayout(self.returnGridLayout(start=5, end=8))
        self.tabWidget.addTab(tab2, "Inputs 5-8")

    def initUI(self):
        self.mainLayout.addWidget(self.tabWidget)

    def initConnections(self):
        for checkbox, comboBox, stacked_widget in zip(self.active_checkboxes, self.combo_boxes, self.stacked_widgets):
            checkbox.toggled.connect(lambda state, c=comboBox, s=stacked_widget: self.toggleCapture(state, c, s))
            comboBox.currentIndexChanged.connect(self.inputComboBoxChanged)
        self.videoHubData.tally_SIGNAL.connect(self.getTally)

    def returnGridLayout(self, start=1, end=4):
        gridLayout = QGridLayout()
        for i in range(start, end + 1):
            label = QLabel(f"Input_{i}")
            label.setFont(QFont("Arial", 12, QFont.Weight.Bold))

            combo = QComboBox(self)
            combo.setFixedSize(150, 30)
            combo.addItems(self.generator_list)
            combo.currentIndexChanged.connect(self.inputComboBoxChanged)

            stacked_widget = QStackedWidget(self)
            placeholder_widget = QLabel("Select an option")
            stacked_widget.addWidget(placeholder_widget)

            btnInputAssign = QCheckBox("Active")

            gridLayout.addWidget(label, i - start, 0)
            gridLayout.addWidget(combo, i - start, 1)
            gridLayout.addWidget(stacked_widget, i - start, 2)
            gridLayout.addWidget(btnInputAssign, i - start, 3)

            self.combo_boxes.append(combo)
            self.stacked_widgets.append(stacked_widget)
            self.active_checkboxes.append(btnInputAssign)

        return gridLayout

    def inputComboBoxChanged(self, index):
        if index == 0:
            return
        sender = self.sender()
        stack_index = self.combo_boxes.index(sender)
        stacked_widget = self.stacked_widgets[stack_index]
        selected_input = sender.currentText()

        input_position = stack_index  + 1

        # Rimuovi l'InputDevice esistente se non è l'input nero predefinito
        existing_device = self.videoHubData.getInputDevice(input_position)
        if existing_device and existing_device != self.videoHubData.returnDefaultBlackInput():
            self.videoHubData.removeInputDevice(input_position)

        # Crea il nuovo InputDevice in base al tipo selezionato
        inputDevice = None
        if selected_input == "colorGenerator":
            inputDevice = InputDevice_ColorGenerator(input_position, self)
        elif selected_input == "noiseGenerator":
            inputDevice = InputDevice_NoiseGenerator(input_position,  self)
        elif selected_input == "stillImage":
            inputDevice = InputDevice_StillImagePlayer(input_position, self)
        elif selected_input == "smpteBarsGenerator":
            inputDevice = InputDevice_SmpteGenerator(input_position, self)
        elif selected_input == "desktopCapture":
            inputDevice = InputDevice_DesktopCapture(input_position, self)
        elif selected_input == "cameraCapture":
            inputDevice = InputDevice_CameraCapture(input_position, self)

        if inputDevice:
            # Aggiungi l'InputDevice al VideoHubData
            self.videoHubData.addInputDevice(input_position, inputDevice)

            # Rimuovi i widget precedenti dallo stacked_widget (se presenti)
            for i in reversed(range(1, stacked_widget.count())):
                widget_to_remove = stacked_widget.widget(i)
                stacked_widget.removeWidget(widget_to_remove)
                widget_to_remove.deleteLater()
            # Aggiungi la graphicInterface dell'InputDevice allo stacked_widget
            stacked_widget.addWidget(inputDevice.graphicInterface)
            # Imposta l'indice corrente sul nuovo widget
            stacked_widget.setCurrentIndex(1)
        else:
            # Torna al widget segnaposto
            stacked_widget.setCurrentIndex(0)

    def toggleCapture(self, state, comboBox, stacked_widget):
        input_index = self.combo_boxes.index(comboBox)+1
        if state:  # Se l'utente attiva l'input
            logging.info(f"Activating input {input_index}")
            self.videoHubData.startInputDevice(input_index)
            comboBox.setEnabled(False)
        else:  # Se l'utente disattiva l'input
            logging.info(f"Deactivating input {input_index}")
            self.videoHubData.stopInputDevice(input_index)
            # Abilita la ComboBox
            comboBox.setEnabled(True)
        self.printVideoHubContent()

    def getTally(self, tally_data):
        logging.info(f"VIDEOHUBWIDGET -Received tally data: {tally_data}")
        sender = tally_data.get('sender')
        if sender != 'videoHub':
            cmd = tally_data.get('cmd')
            position = tally_data.get('position')
            if cmd == 'inputAdded':
                logging.info(f"Input added at position {position}")
            elif cmd == 'inputRemoved':
                logging.info(f"VIDEOHUBWIDGET -Input removed from position {position}")
            else:
                logging.warning(f"VIDEOHUBWIDGET -Invalid command from VideoHub: {cmd}\n{tally_data}")

    def printVideoHubContent(self):
        logging.info("VIDEOHUBWIDGET -Video Hub content:")
        for index, _input in self.videoHubData.videoHubMatrix.items():
            logging.info(f"Input {index}: {_input.getName()} - Type: {_input.getType()}")

    def blockSignals(self, block):
        """
        Metodo helper per disabilitare/abilitare i segnali dei widget.
        """
        for combo_box in self.combo_boxes:
            combo_box.blockSignals(block)
        for checkbox in self.active_checkboxes:
            checkbox.blockSignals(block)


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    videoHubData = VideoHubData018()
    widget = VideoHubWidget018(videoHubData)
    widget.show()
    app.exec()
