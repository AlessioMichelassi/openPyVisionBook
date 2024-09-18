import sys
import logging
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

# Assicurati che questi import siano corretti o sostituiscili con alternative se necessario
from cap5.cap5_9.MrKeyboard.mixerKeyboard.blinkingButton import BlinkingButton
from cap5.cap5_9.MrKeyboard.styles.btnStyle import btnGreenStyle, btnRedStyle, btnCutStyle, btnSpecialStyle
from cap5.cap5_9.MrKeyboard.styles.lblWidget import LblWidget

logging.basicConfig(level=logging.DEBUG)


class MixerKeyboard(QWidget):
    tally_SIGNAL = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.shift_offset = 0  # 0 per 1-4, 4 per 5-8
        self.currentPreview = 1  # Preview starts with input 1 selected
        self.currentProgram = 2  # Program starts con input 2 selected

        self.inputList = ["1", "2", "3", "4"]
        self.lblInputList = ["", "Input 1", "Input 2", "Input 3", "Input 4"]
        self.previewBtnList = []
        self.programBtnList = []
        self.btnCut = QPushButton("CUT")
        self.btnAutoMix = BlinkingButton("AutoMix")
        self.sliderFade = QSlider(Qt.Orientation.Vertical)

        self.cmbEffect = QComboBox(self)
        self.cmbEffect.addItems(["Fade", "Wipe Left to Right", "Wipe Right to Left",
                                 "Wipe Top to Bottom", "Wipe Bottom to Top", "Stinger1", "Still1"])
        self.lineEditDuration = QLineEdit("1000")
        self.autoMix_TIMER = QTimer(self)
        # init variables for autoMix
        self.steps = 100
        self.step_interval = 100

        # init interface
        self.initUI()
        self.initStyle()
        self.initGeometry()
        self.initConnections()

        # Set initial state
        self.initInitialState()

    def initUI(self):
        mainLayout = QHBoxLayout()
        leftLayout = QVBoxLayout()
        inputNameLayout = self.createLineEditRow("input", [])
        previewLayout = self.createButtonRow("prw", self.previewBtnList)

        programLayout = self.createButtonRow("prg", self.programBtnList)
        leftLayout.addLayout(inputNameLayout)
        leftLayout.addLayout(previewLayout)
        leftLayout.addLayout(programLayout)

        centerLayout = QVBoxLayout()
        centerLayout.addWidget(self.sliderFade)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.btnCut)
        controlLayout.addWidget(self.btnAutoMix)
        effectLayout = QVBoxLayout()
        effectLayout.addWidget(self.lineEditDuration)
        effectLayout.addWidget(self.cmbEffect)
        rightLayout = QVBoxLayout()
        rightLayout.addLayout(effectLayout)
        rightLayout.addLayout(controlLayout)

        mainLayout.addLayout(leftLayout)
        mainLayout.addLayout(centerLayout)
        mainLayout.addLayout(rightLayout)

        self.setLayout(mainLayout)

    def createButtonRow(self, prefixName, buttonList):
        btnLayout = QHBoxLayout()
        if prefixName == "prw":
            self.btnShift = QPushButton("Shift")
            self.btnShift.setCheckable(True)
            self.btnShift.setChecked(False)
            self.btnShift.setStyleSheet(btnSpecialStyle)
            btnLayout.addWidget(self.btnShift)
        elif prefixName == "prg":
            self.btnCtrl = QPushButton("Ctrl")
            self.btnCtrl.setCheckable(True)
            self.btnCtrl.setChecked(False)
            self.btnCtrl.setStyleSheet(btnSpecialStyle)
            btnLayout.addWidget(self.btnCtrl)
        for i in range(len(self.inputList)):
            btn = QPushButton()
            btn.setObjectName(f"{prefixName}_btn_{i}")
            btn.setText(self.inputList[i])  # Imposta il testo del pulsante
            btn.setCheckable(True)
            btn.setChecked(False)

            if prefixName == "prw":
                btn.clicked.connect(self.onPreviewButtonClicked)
                btn.setStyleSheet(btnGreenStyle)
            elif prefixName == "prg":
                btn.clicked.connect(self.onProgramButtonClicked)
                btn.setStyleSheet(btnRedStyle)

            buttonList.append(btn)
            btnLayout.addWidget(btn)
        return btnLayout

    def createLineEditRow(self, prefixName, lineEditList):
        leLayout = QHBoxLayout()
        for i in range(len(self.lblInputList)):
            le = LblWidget(prefixName, i, (100, 30))
            le.setObjectName(f"Input_lbl_{i}")
            le.returnPressed.connect(self.onLineEditNickNameChanged)
            le.setText(self.lblInputList[i])
            lineEditList.append(le)
            leLayout.addWidget(le)
        return leLayout

    def initGeometry(self):
        self.sliderFade.setRange(0, 100)

    def initStyle(self):
        self.btnAutoMix.setStyleSheet(btnCutStyle)
        self.btnCut.setStyleSheet(btnCutStyle)

    def initConnections(self):
        self.autoMix_TIMER.timeout.connect(self.faderAnimation)
        self.btnCut.clicked.connect(self.onCut)
        self.btnAutoMix.clicked.connect(self.onAutoMix)
        self.btnAutoMix.setBlinkingTimeOut(int(int(self.lineEditDuration.text()) / 100))
        self.sliderFade.valueChanged.connect(self.onFade)
        self.cmbEffect.currentIndexChanged.connect(self.onEffectChange)
        self.btnShift.clicked.connect(self.onShift)
        self.btnCtrl.clicked.connect(self.onCtrl)

    def initInitialState(self):
        self.updateButtonStates()

    def onPreviewButtonClicked(self):
        btn = self.sender()
        number = int(btn.text())  # Usa il testo del pulsante come numero
        self.currentPreview = number
        self.updateButtonStates()
        self.emitTallySignal(cmd='previewChange')

    def onProgramButtonClicked(self):
        btn = self.sender()
        number = int(btn.text())  # Usa il testo del pulsante come numero
        self.currentProgram = number
        self.updateButtonStates()
        self.emitTallySignal(cmd='programChange')

    def updateButtonStates(self):
        # Deseleziona tutti i pulsanti
        for btn in self.previewBtnList + self.programBtnList:
            btn.setChecked(False)

        # Calcola l'offset
        offset = self.shift_offset

        # Assicurati che currentPreview e currentProgram siano nel range corretto
        preview_index = self.currentPreview - 1 - offset
        program_index = self.currentProgram - 1 - offset

        if 0 <= preview_index < len(self.previewBtnList):
            self.previewBtnList[preview_index].setChecked(True)
        if 0 <= program_index < len(self.programBtnList):
            self.programBtnList[program_index].setChecked(True)

    def emitTallySignal(self, cmd):
        tally_status = {
            'sender': 'keyboard',
            'cmd': cmd,
            'preview': str(self.currentPreview),
            'program': str(self.currentProgram),
            'effect': self.cmbEffect.currentText(),
            'fade': self.sliderFade.value() / 100.0
        }
        logging.info(f"MR KEYBOARD EMIT TALLY SIGNAL: {tally_status}")
        self.tally_SIGNAL.emit(tally_status)

    def onLineEditNickNameChanged(self):
        le = self.sender()
        print(f"LineEdit {le.objectName()} changed to {le.text()}")
        number = int(le.objectName().split("_")[-1])
        nickName = le.text()
        tally_status = {
            'sender': 'keyboard',
            'cmd': 'nickNameChanged',
            'position': number,
            'nickName': nickName
        }
        logging.info(f"MR KEYBOARD EMIT TALLY SIGNAL: {tally_status}")
        self.tally_SIGNAL.emit(tally_status)

    def onCut(self):
        # Swap the preview and program inputs
        self.currentPreview, self.currentProgram = self.currentProgram, self.currentPreview
        # Update button states
        self.updateButtonStates()
        self.emitTallySignal(cmd='cut')  # Emit a 'cut' command
        self.sliderFade.valueChanged.disconnect(self.onFade)
        self.sliderFade.setValue(0)
        self.sliderFade.valueChanged.connect(self.onFade)

    def onAutoMix(self):
        self.btnAutoMix.startBlinking()
        self.emitTallySignal(cmd='auto')  # Emit an 'auto' command
        try:
            duration = int(self.lineEditDuration.text())
        except ValueError:
            duration = 100  # Default to 100ms if invalid input
            self.lineEditDuration.setText("100")

        self.steps = 100  # Number of steps to move the slider
        self.step_interval = duration // self.steps  # Interval per step in ms
        if not self.autoMix_TIMER.isActive():
            self.sliderFade.valueChanged.disconnect(self.onFade)
            self.autoMix_TIMER.start(self.step_interval)

    def faderAnimation(self):
        if self.steps > 0:
            self.sliderFade.setValue(self.sliderFade.value() + 1)
            self.steps -= 1
        else:
            self.autoMix_TIMER.stop()
            # Swap the preview and program inputs
            self.currentPreview, self.currentProgram = self.currentProgram, self.currentPreview

            # Update button states
            self.updateButtonStates()
            self.sliderFade.setValue(0)
            self.sliderFade.valueChanged.connect(self.onFade)

    def onFade(self, value):
        print(f"Fade level: {value}")
        self.emitTallySignal(cmd='faderChange')  # Emit a 'faderChange' command

    def onEffectChange(self, index):
        print(f"Effect changed to: {self.cmbEffect.currentText()}")
        self.emitTallySignal(cmd='effectChange')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.onAutoMix()
        elif event.key() == Qt.Key.Key_C:
            self.onCut()

    def getTally(self, tally_status):
        logging.info(f"MR KEYBOARD GET TALLY SIGNAL: {tally_status}")
        cmd = tally_status['cmd']
        if cmd in ['cut', 'auto', 'faderChange', 'effectChange']:
            """Aggiorna lo stato del tastierino basato sul segnale di tally ricevuto."""
            self.currentPreview = int(tally_status['preview'])
            self.currentProgram = int(tally_status['program'])
            self.cmbEffect.setCurrentText(tally_status['effect'])
            self.sliderFade.setValue(int(float(tally_status['fade']) * 100))

            # Aggiorna lo stato dei pulsanti senza emettere segnali di tally
            self.updateButtonStates()
        elif cmd == 'nickNameChanged':
            position = int(tally_status['position'])
            nickName = tally_status['nickName']
            self.findChild(LblWidget, f"Input_lbl_{position}").setText(nickName)

    def onShift(self):
        if self.btnShift.isChecked():
            # Mostra i tasti da 5 a 8
            self.inputList = ["5", "6", "7", "8"]
            self.lblInputList = ["Input 5", "Input 6", "Input 7", "Input 8"]
            self.shift_offset = 4
        else:
            # Torna ai tasti da 1 a 4
            self.inputList = ["1", "2", "3", "4"]
            self.lblInputList = ["Input 1", "Input 2", "Input 3", "Input 4"]
            self.shift_offset = 0
        # Aggiorna i pulsanti
        self.updateButtonTexts()
        self.updateLabels()
        self.updateButtonStates()

    def onCtrl(self):
        if self.btnCtrl.isChecked():
            # Esempio: Attiva una modalità speciale
            logging.info("Ctrl premuto: Modalità speciale attivata.")
            # Implementa la logica desiderata
        else:
            # Disattiva la modalità speciale
            logging.info("Ctrl rilasciato: Modalità speciale disattivata.")
            # Implementa la logica desiderata

    def updateLabels(self):
        for i in range(len(self.lblInputList)):
            self.findChild(LblWidget, f"Input_lbl_{i}").setText(self.lblInputList[i])

    def updateButtonTexts(self):
        for i, btn in enumerate(self.previewBtnList):
            btn.setText(self.inputList[i])
        for i, btn in enumerate(self.programBtnList):
            btn.setText(self.inputList[i])

    def closeEvent(self, event):
        self.autoMix_TIMER.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MixerKeyboard()
    window.tally_SIGNAL.connect(print)
    window.show()

    # Simula il ricevimento di un segnale di tally esterno
    external_tally = {
        'cmd': 'cut',
        'preview': '4',
        'program': '1',
        'effect': 'Wipe Left to Right',
        'fade': 0.5
    }
    window.getTally(external_tally)
    nick_nameTest = {
        'cmd': 'nickNameChanged',
        'position': '2',
        'nickName': 'Camera 2'
    }
    window.getTally(nick_nameTest)
    sys.exit(app.exec())
