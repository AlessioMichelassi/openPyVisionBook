import cv2
from PyQt6.QtCore import *
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import *

from cap2.cap2_6.synchObject import SynchObject
from cap3.cap3_1.colorGenerator import ColorGenerator
from cap3.cap3_1.randomNoiseGenerator import RandomNoiseGenerator
from cap4.cap4_5.stingerInputLoader_02_thread import StingerDisplay
from cap4.cap4_8.mixBus4_8 import MixBus4_8, MIX_TYPE
from cap4.cap4_8.openGLViewer import OpenGLViewer
from cap4.cap4_8.stingerLoader import StingerLoaderThread


class testMixBus5_8(QWidget):
    def __init__(self, synchObject, loaderThread, parent=None):
        super().__init__(parent)
        self.syncObject = synchObject
        self.input1 = ColorGenerator(self.syncObject)
        self.input2 = RandomNoiseGenerator(self.syncObject)
        self.mixBus = MixBus4_8(self.input1, self.input2, loaderThread)
        self.prw_image = QImage()
        self.prg_image = QImage()
        self.previewViewer = OpenGLViewer()
        self.programViewer = OpenGLViewer()
        self.btnCut = QPushButton("CUT")
        self.btnAutoMix = QPushButton("AutoMix")
        self.sldFade = QSlider()
        self.cmbEffect = QComboBox()
        self.cmbEffect.addItems(["Fade", "Wipe Left to Right", "Wipe Right to Left",
                                 "Wipe Top to Bottom", "Wipe Bottom to Top", "Stinger"])
        self.sldFade.setOrientation(Qt.Orientation.Horizontal)
        self.sldFade.setRange(0, 100)
        self.initUI()
        self.initGeometry()
        self.initConnections()

    def initUI(self):
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
        self.setLayout(mainLayout)

    def initGeometry(self):
        self.previewViewer.setFixedSize(1920, 1080)
        self.programViewer.setFixedSize(1920, 1080)

    def initConnections(self):
        self.syncObject.synch_SIGNAL.connect(self.updateFrame)
        self.btnCut.clicked.connect(self.cut)
        self.btnAutoMix.clicked.connect(self.autoMix)
        self.sldFade.valueChanged.connect(self.setFade)
        self.cmbEffect.currentIndexChanged.connect(self.setEffect)

    def updateFrame(self):
        prw_frame, prg_frame = self.mixBus.getMixed()
        #prw_frame = cv2.resize(prw_frame, (640, 360))
        #prg_frame = cv2.resize(prg_frame, (640, 360))
        self.prw_image = QImage(prw_frame.data, prw_frame.shape[1], prw_frame.shape[0], QImage.Format.Format_BGR888)
        self.prg_image = QImage(prg_frame.data, prg_frame.shape[1], prg_frame.shape[0], QImage.Format.Format_BGR888)
        self.previewViewer.setImage(self.prw_image)
        self.programViewer.setImage(self.prg_image)

    def cut(self):
        self.mixBus.cut()

    def autoMix(self):
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


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    path = r'/cap4/cap4_5/stingerDefault'
    loaderThread = StingerLoaderThread(path)
    synchObject = SynchObject()
    stingerDisplay = StingerDisplay(loaderThread)
    stingerDisplay.show()
    test = testMixBus5_8(synchObject, loaderThread)
    test.show()
    sys.exit(app.exec())
