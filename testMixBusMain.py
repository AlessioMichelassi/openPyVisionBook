import cv2
from PyQt6.QtCore import *
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import *


from cap5.mainDir.data.dataManager import DataManager
from cap5.mainDir.inputs.colorGenerator import ColorGenerator
from cap5.mainDir.inputs.randomNoiseGenerator import RandomNoiseGenerator
from cap5.mainDir.inputs.synchObject import SynchObject
from cap5.mainDir.mixBus.mixBusMain import MixBusMain, MIX_TYPE
from cap5.mainDir.mixBus.stingerInputLoader_02_thread import StingerLoaderThread, StingerDisplay
from cap5.mainDir.outputs.openGLViewer import OpenGLViewer


class testMixBus5_8(QWidget):
    def __init__(self, _synchObject, parent=None):
        super().__init__(parent)
        # init external widgets
        self.syncObject = _synchObject
        self.input1 = ColorGenerator(self.syncObject)
        self.input2 = RandomNoiseGenerator(self.syncObject)
        self.mixBus = MixBusMain(self.input1, self.input2)
        self.dataManager = DataManager()
        # init internal widgets
        self.prw_image = QImage()
        self.prg_image = QImage()
        self.previewViewer = OpenGLViewer()
        self.programViewer = OpenGLViewer()
        self.btnCut = QPushButton("CUT")
        self.btnAutoMix = QPushButton("AutoMix")
        self.sldFade = QSlider()
        self.cmbEffect = QComboBox(self)
        self.lblFrameRate = QLabel("Frame Rate: 0.0")
        # init UI
        self.initUI()
        self.initGeometry()
        self.initConnections()

    def initUI(self):
        """
        This function initializes the UI.
        :return:
        """
        mainLayout = QVBoxLayout()
        viewerLayout = QHBoxLayout()
        viewerLayout.addWidget(self.previewViewer)
        viewerLayout.addWidget(self.programViewer)
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        buttonLayout = QHBoxLayout()
        buttonLayout.addItem(spacer)
        buttonLayout.addWidget(self.btnCut)
        buttonLayout.addWidget(self.btnAutoMix)
        buttonLayout.addWidget(self.sldFade)
        buttonLayout.addWidget(self.cmbEffect)
        mainLayout.addLayout(viewerLayout)
        mainLayout.addLayout(buttonLayout)
        mainLayout.addWidget(self.lblFrameRate)
        self.setLayout(mainLayout)

    def initGeometry(self):
        self.previewViewer.setFixedSize(640, 360)
        self.programViewer.setFixedSize(640, 360)
        self.cmbEffect.addItems(["Fade", "Wipe Left to Right", "Wipe Right to Left",
                                 "Wipe Top to Bottom", "Wipe Bottom to Top", "Stinger", "Still"])
        self.sldFade.setOrientation(Qt.Orientation.Horizontal)
        self.sldFade.setRange(0, 100)

    def initConnections(self):
        self.syncObject.synch_SIGNAL.connect(self.updateFrame)
        self.btnCut.clicked.connect(self.cut)
        self.btnAutoMix.clicked.connect(self.autoMix)
        self.sldFade.valueChanged.connect(self.setFade)
        self.cmbEffect.currentIndexChanged.connect(self.setEffect)
        self.dataManager.errorSignal.connect(self.handleError)
        self.dataManager.statusSignal.connect(print)
        self.dataManager.readySignal.connect(self.initData)
        self.dataManager.loadData()

    def initData(self):
        self.mixBus.setStinger(self.dataManager.stingerObject)
        self.mixBus.setStill(self.dataManager.stillObject)

    def handleError(self, error):
        print(f"Error: {error}")

    def updateFrame(self):
        prw_frame, prg_frame = self.mixBus.getMixed()
        self.lblFrameRate.setText(f"Frame Rate: {self.mixBus.get_fps():.2f}")
        self.prw_image = QImage(prw_frame.data, prw_frame.shape[1], prw_frame.shape[0], QImage.Format.Format_BGR888)
        self.prg_image = QImage(prg_frame.data, prg_frame.shape[1], prg_frame.shape[0], QImage.Format.Format_BGR888)
        self.sldFade.setOrientation(Qt.Orientation.Horizontal)
        self.sldFade.setRange(0, 100)
        self.previewViewer.setImage(self.prw_image)
        self.programViewer.setImage(self.prg_image)

    def cut(self):
        self.mixBus.cut()

    def autoMix(self):
        print(f"debug: {self.sldFade.value()} fade: {self.cmbEffect.currentText()}")
        self.mixBus.autoMix()

    def setFade(self):
        self.mixBus.setFade(self.sldFade.value())

    def setEffect(self):
        effect = self.cmbEffect.currentText()
        if effect == "Fade":
            self.mixBus.effectType = MIX_TYPE.FADE
        elif effect == "Wipe Left to Right":
            self.mixBus.effectType = MIX_TYPE.WIPE_LEFT_TO_RIGHT
        elif effect == "Wipe Right to Left":
            self.mixBus.effectType = MIX_TYPE.WIPE_RIGHT_TO_LEFT
        elif effect == "Wipe Top to Bottom":
            self.mixBus.effectType = MIX_TYPE.WIPE_TOP_TO_BOTTOM
        elif effect == "Wipe Bottom to Top":
            self.mixBus.effectType = MIX_TYPE.WIPE_BOTTOM_TO_TOP
        elif effect == "Stinger":
            self.mixBus.effectType = MIX_TYPE.WIPE_STINGER
        elif effect == "Still":
            self.mixBus.effectType = MIX_TYPE.FADE_STILL


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    synchObject = SynchObject()
    test = testMixBus5_8(synchObject)
    test.show()
    sys.exit(app.exec())
