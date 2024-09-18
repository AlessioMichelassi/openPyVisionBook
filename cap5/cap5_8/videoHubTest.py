import sys
import time
import logging
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import QMutex, QMutexLocker, QMetaObject, Qt, Q_ARG, QThreadPool, QTimer, pyqtSlot
from PyQt6.QtGui import QFont

from cap5.cap5_3.videoHub.videoHubData018 import VideoHubData018
from cap5.cap5_8.mixBus015 import  MixBus016  # Adjust the import path as necessary
from cap5.cap5_3.videoHub.videoHubWidget_18 import VideoHubWidget018
from cap5.cap5_8.openGLViewer015 import OpenGLViewer015  # Adjust the import path as necessary

# Configure logging
logging.basicConfig(level=logging.INFO)


class videoHubTest(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VideoHub Test")
        self.setGeometry(100, 100, 1280, 720)

        # Viewers for preview and program outputs
        self.previewViewer = OpenGLViewer015()
        self.previewViewer.setMinimumSize(640, 360)
        self.programViewer = OpenGLViewer015()
        self.programViewer.setMinimumSize(640, 360)

        # Label to display FPS
        self.lblFps = QLabel("FPS: 0", self)
        self.lblFps.setFont(QFont("Arial", 12, QFont.Weight.Bold))

        # VideoHub data and widget
        self.videoHubData = VideoHubData018()
        self.videoHubWidget = VideoHubWidget018(self.videoHubData)

        # Input selection combo boxes
        self.cmbPreviewInput = QComboBox(self)
        self.cmbPreviewInput.addItems([
            "Input 1", "Input 2", "Input 3", "Input 4",
            "Input 5", "Input 6", "Input 7", "Input 8"
        ])
        self.cmbProgramInput = QComboBox(self)
        self.cmbProgramInput.addItems([
            "Input 1", "Input 2", "Input 3", "Input 4",
            "Input 5", "Input 6", "Input 7", "Input 8"
        ])

        # Initialize MixBus
        self.mixBus = MixBus016(self.videoHubData)

        # Connect MixBus frame_ready signal
        self.mixBus.frame_ready.connect(self.handle_frame_ready)

        # Mutex for thread safety
        self.input_mutex = QMutex()

        # Initialize UI and connections
        self.initUI()
        self.initConnections()

        # Start the MixBus loop
        self.next_call = time.perf_counter()
        self.mixBusLoop()

    def initUI(self):
        mainLayout = QVBoxLayout(self)

        # Layout for the viewers
        viewer_layout = QHBoxLayout()
        viewer_layout.addWidget(self.previewViewer)
        viewer_layout.addWidget(self.programViewer)
        mainLayout.addLayout(viewer_layout)

        # FPS label
        mainLayout.addWidget(self.lblFps)

        # Central layout with VideoHub widget and input selection
        central_layout = QHBoxLayout()
        central_layout.addWidget(self.videoHubWidget)

        # Input selection layout
        input_selection_layout = QVBoxLayout()
        input_selection_layout.addWidget(QLabel("Select Preview Input:"))
        input_selection_layout.addWidget(self.cmbPreviewInput)
        input_selection_layout.addWidget(QLabel("Select Program Input:"))
        input_selection_layout.addWidget(self.cmbProgramInput)
        central_layout.addLayout(input_selection_layout)

        mainLayout.addLayout(central_layout)
        self.setLayout(mainLayout)

    def initConnections(self):
        self.cmbPreviewInput.currentIndexChanged.connect(self.onPreviewInputChanged)
        self.cmbProgramInput.currentIndexChanged.connect(self.onProgramInputChanged)

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
        # Update the viewers with the new frames
        if prw_frame is not None:
            self.previewViewer.setFrame(prw_frame)
        if prg_frame is not None:
            self.programViewer.setFrame(prg_frame)
        self.lblFps.setText(f"FPS: {fps:.2f}")

    def onPreviewInputChanged(self):
        index = self.cmbPreviewInput.currentIndex() + 1  # Inputs are 1-indexed
        new_preview_input = self.videoHubData.getInputDevice(index)
        with QMutexLocker(self.mixBus.input_mutex):
            self.mixBus.actualPreviewIndex = index
            self.mixBus.previewInput = new_preview_input
        logging.info(f"Preview input changed to Input {index}")

    def onProgramInputChanged(self):
        index = self.cmbProgramInput.currentIndex() + 1  # Inputs are 1-indexed
        new_program_input = self.videoHubData.getInputDevice(index)
        with QMutexLocker(self.mixBus.input_mutex):
            self.mixBus.actualProgramIndex = index
            self.mixBus.programInput = new_program_input
        logging.info(f"Program input changed to Input {index}")

    def closeEvent(self, event):
        # Stop MixBus processing
        self.mixBus.stop()
        QThreadPool.globalInstance().waitForDone()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = videoHubTest()
    window.show()
    sys.exit(app.exec())
