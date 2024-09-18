# Version: 2024.09.03

import logging
import time
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class ProgressDisplay(QWidget):
    def __init__(self, workerThread, title="Operation Progress", message="Operation in progress...", parent=None):
        super().__init__(parent)
        self.workerThread = workerThread
        self.progressBar = QProgressBar(self)
        self.lbl = QLabel(message, self)
        self.timeLabel = QLabel("Time: 0.0s", self)
        self.timer = QTimer(self)
        self.startTime = time.time()
        self.initUI(title)
        self.initConnections()
        self.timer.start(100)

    def initUI(self, title):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.lbl)
        mainLayout.addWidget(self.progressBar)
        mainLayout.addWidget(self.timeLabel)
        self.setLayout(mainLayout)
        self.setWindowTitle(title)
        self.progressBar.setRange(0, 100)

    def initConnections(self):
        self.workerThread.progressUpdated.connect(self.updateProgressBar)
        self.timer.timeout.connect(self.animateProgressBar)

    @pyqtSlot(int)
    def updateProgressBar(self, progress):
        self.progressBar.setValue(progress)

    @pyqtSlot()
    def animateProgressBar(self):
        elapsed_time = time.time() - self.startTime
        self.timeLabel.setText(f"Time: {elapsed_time:.1f}s")

    @pyqtSlot()
    def onOperationCompleted(self):
        self.timer.stop()
        self.progressBar.setValue(100)
        elapsed_time = time.time() - self.startTime
        self.timeLabel.setText(f"Completed in: {elapsed_time:.1f}s")
        logging.info("Operation completed!")
        QTimer.singleShot(1000, self.close)
