from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from cap5.cap5_3.videoHub.videoHubData018 import VideoHubData018
from cap5.mainDir.outputs.openGLViewer import OpenGLViewer
from cap5.cap5_3.videoHub.videoHubWidget_18 import VideoHubWidget018


class videoHubTest(QWidget):
    def __init__(self):
        super().__init__()
        self.liveInputIndex = 0
        self.mainViewer = OpenGLViewer()
        self.mainViewer.setMinimumSize(640, 360)
        self.videoHubData = VideoHubData018()
        self.videoHubWidget = VideoHubWidget018(self.videoHubData)
        self.cmbInputType = QComboBox(self)
        self.cmbInputType.addItems(["Select input", "input_1", "input_2", "input_3", "input_4",
                                    "input_5", "input_6", "input_7", "input_8"])
        self.uiTimer = QTimer(self)
        self.uiTimer.timeout.connect(self.updateUI)
        self.initUI()
        self.initConnections()

    def initUI(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.mainViewer)
        central_layout = QHBoxLayout(self)
        central_layout.addWidget(self.videoHubWidget)
        central_layout.addWidget(self.cmbInputType)
        mainLayout.addLayout(central_layout)
        self.setLayout(mainLayout)

    def initConnections(self):
        self.cmbInputType.currentIndexChanged.connect(self.onInputTypeChanged)
        self.uiTimer.start(1000//60)

    def updateUI(self):
        inputDevice = self.videoHubData.getInputDevice(self.liveInputIndex)
        frame = inputDevice.getFrame()
        qImage = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format.Format_BGR888)
        self.mainViewer.setImage(qImage)

    def onInputTypeChanged(self):
        self.liveInputIndex = self.cmbInputType.currentIndex()


if __name__ == "__main__":
    app = QApplication([])
    window = videoHubTest()
    window.show()
    app.exec()

