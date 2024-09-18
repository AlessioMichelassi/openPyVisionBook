import time

import numpy as np
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
import sys

from cap5.cap5_3.videoHub.videoHubData018 import VideoHubData018
from cap5.cap5_3.videoHub.videoHubWidget_18 import VideoHubWidget018
from cap5.cap5_4.tallyManager import TallyManager
from cap5.cap5_8.mixBus015 import MixBus016
from cap5.cap5_8.openGLViewer015 import OpenGLViewer015
from cap5.cap5_9.MrKeyboard.mixingKeyboard import MixerKeyboard


class MixEffect016(QWidget):
    frame_ready = pyqtSignal(np.ndarray, np.ndarray, float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.txtServerMessage = QTextEdit(self)
        self.mainTab = QTabWidget()
        self.mixerKeyboard = MixerKeyboard(self)
        self.tallyManager = TallyManager(self)
        self.videoHubData = VideoHubData018(self)
        self.videoHubWidget = VideoHubWidget018(self.videoHubData)
        # Initialize MixBus
        self.mixBus = MixBus016(self.videoHubData)
        # Connect MixBus frame_ready signal
        self.mixBus.frame_ready.connect(self.handle_frame_ready)
        # Mutex for thread safety
        self.input_mutex = QMutex()

        self.initUI()
        self.initConnections()
        self.initGeometry()
        # Start the MixBus loop
        self.next_call = time.perf_counter()
        self.mixBusLoop()

    def closeEvent(self, event, *args, **kwargs):
        event.accept()

    def initUI(self):
        self.txtServerMessage.setReadOnly(True)
        mainLayout = QVBoxLayout()
        central_layout = QVBoxLayout()
        central_layout.addStretch()
        mainLayout.addLayout(central_layout)
        lower_layout = QHBoxLayout()
        self.mainTab.addTab(self.videoHubWidget, "Video Hub")
        self.mainTab.addTab(self.txtServerMessage, "Server Messages")
        lower_layout.addWidget(self.mainTab)
        mixerLayout = QVBoxLayout()
        mixerLayout.addStretch()
        mixerLayout.addWidget(self.mixerKeyboard)
        lower_layout.addLayout(mixerLayout)
        mainLayout.addLayout(lower_layout)
        self.setLayout(mainLayout)

    def initConnections(self):
        # invia i segnali a tally manager
        self.mixerKeyboard.tally_SIGNAL.connect(self.tallyManager.parseTallySignal)
        self.videoHubWidget.videoHubData.tally_SIGNAL.connect(self.tallyManager.parseTallySignal)
        # invia i segnali del tally ai vari elementi
        self.tallyManager.mixBus_SIGNAL.connect(self.mixBus.getTally)

    def initGeometry(self):
        self.setWindowTitle("MixEffect")

    def mixBusLoop(self):
        # Call mixBus.getMixed() to process frames
        self.mixBus.getMixed()

        # Schedule the next call
        self.next_call += 1 / 62
        # Targeting 60 FPS
        delay = max(0, self.next_call - time.perf_counter())
        QMetaObject.invokeMethod(
            self, "scheduleNextMixBusLoop", Qt.ConnectionType.QueuedConnection,
            Q_ARG(float, delay)
        )

    @pyqtSlot(float)
    def scheduleNextMixBusLoop(self, delay):
        # Schedule the mixBusLoop to run after 'delay' seconds
        QTimer.singleShot(int(delay * 1000), self.mixBusLoop)

    def handle_frame_ready(self, prw_frame, prg_frame, fps):
        self.frame_ready.emit(prw_frame, prg_frame, fps)

    def serialize(self):
        return self.videoHubData.serialize()

    def deserialize(self, data):
        self.videoHubData.deserialize(data)
        #self.videoHubWidget.deserialize(data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    testWindow = MixEffect016()
    testWindow.show()
    sys.exit(app.exec())
