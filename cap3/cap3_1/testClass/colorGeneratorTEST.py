import time

import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from cap2.cap2_6.synchObject import SynchObject
from cap3.cap3_1.colorGenerator import ColorGenerator


class VideoApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        # init internal widget
        self.widget = QWidget()
        self.viewer = QLabel()
        self.fpsLabel = QLabel("FPS: 0.00")  # Initialize FPS label
        self.displayLabel = QLabel()

        # init external object
        self.synchObject = SynchObject(60)
        self.input1 = ColorGenerator(self.synchObject)
        # init layout
        self.initLayout()
        # init connections
        self.initConnections()
        # init geometry
        self.initGeometry()
        # init a single shot timer to stop the app after 10 seconds
        QTimer.singleShot(10000, self.stopApp)

    def initLayout(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.viewer)
        mainLayout.addWidget(self.fpsLabel)
        mainLayout.addWidget(self.displayLabel)
        self.widget.setLayout(mainLayout)

    def initConnections(self):
        self.synchObject.synch_SIGNAL.connect(self.displayFrame)

    def initGeometry(self):
        self.viewer.setFixedSize(1920, 1080)
        self.widget.show()

    def displayFrame(self):
        frame = self.input1.getFrame()
        if frame is not None and frame.size != 0:
            start_time = time.time()
            image = QImage(frame.data, frame.shape[1], frame.shape[0],
                           QImage.Format.Format_BGR888)
            self.viewer.setPixmap(QPixmap.fromImage(image))
            display_time = time.time() - start_time
            self.displayLabel.setText(f"Frame displayed in {display_time:.6f} seconds")
            self.fpsLabel.setText(f"FPS: {self.input1.fps:.2f}")  # Update FPS label

    def stopApp(self):
        print(f"Media FPS: {self.input1.fps:.2f}")
        self.exit()


def mainApp():
    app = VideoApp(sys.argv)
    app.exec()


if __name__ == "__main__":
    import sys
    import cProfile
    import pstats
    import io

    pr = cProfile.Profile()
    pr.enable()
    mainApp()
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
