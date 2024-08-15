import cv2
from PyQt6.QtCore import *
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import *

from cap2.cap2_6.synchObject import SynchObject
from cap3.cap3_1.colorGenerator import ColorGenerator
from cap3.cap3_1.randomNoiseGenerator import RandomNoiseGenerator
from cap4.cap4_2.mixBus4_2 import MixBus4_2


class TestMixBus4_2(QWidget):
    def __init__(self, synchObject, parent=None):
        super().__init__(parent)
        self.syncObject = synchObject
        self.input1 = ColorGenerator(self.syncObject)
        self.input2 = RandomNoiseGenerator(self.syncObject)
        self.mixBus = MixBus4_2(self.input1, self.input2)
        self.lblPreview = QLabel()
        self.lblProgram = QLabel()
        self.btnCut = QPushButton("CUT")
        self.btnAutoMix = QPushButton("AutoMix")
        self.sldFade = QSlider()
        self.sldFade.setOrientation(Qt.Orientation.Horizontal)
        self.sldFade.setRange(0, 100)
        self.initUI()
        self.initGeometry()
        self.initConnections()

    def initUI(self):
        mainLayout = QVBoxLayout()
        viewerLayout = QHBoxLayout()
        viewerLayout.addWidget(self.lblPreview)
        viewerLayout.addWidget(self.lblProgram)
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        buttonLayout = QHBoxLayout()
        buttonLayout.addItem(spacer)
        buttonLayout.addWidget(self.btnCut)
        buttonLayout.addWidget(self.btnAutoMix)
        buttonLayout.addWidget(self.sldFade)
        mainLayout.addLayout(viewerLayout)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def initGeometry(self):
        self.lblPreview.setFixedSize(640, 360)
        self.lblProgram.setFixedSize(640, 360)

    def initConnections(self):
        self.syncObject.synch_SIGNAL.connect(self.updateFrame)
        self.btnCut.clicked.connect(self.cut)
        self.btnAutoMix.clicked.connect(self.autoMix)
        self.sldFade.valueChanged.connect(self.fadeTo)

    def updateFrame(self):
        prw_frame, prg_frame = self.mixBus.getMixed()
        prw_frame = cv2.resize(prw_frame, (640, 360))
        prg_frame = cv2.resize(prg_frame, (640, 360))
        prw_image = QImage(prw_frame.data, prw_frame.shape[1], prw_frame.shape[0], QImage.Format.Format_BGR888)
        prg_image = QImage(prg_frame.data, prg_frame.shape[1], prg_frame.shape[0], QImage.Format.Format_BGR888)
        self.lblPreview.setPixmap(QPixmap.fromImage(prw_image))
        self.lblProgram.setPixmap(QPixmap.fromImage(prg_image))

    def cut(self):
        self.mixBus.cut()

    def autoMix(self):
        self.mixBus.autoMix()

    def fadeTo(self):
        self.mixBus.setFade(self.sldFade.value())


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    synchObject = SynchObject()
    test = TestMixBus4_2(synchObject)
    test.show()
    sys.exit(app.exec())