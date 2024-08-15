import time

import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *

from cap2.cap2_6.synchObject import SynchObject
from cap3.cap3_9.randomNoiseGenerator import RandomNoiseGenerator
from cap3.cap3_9.test.openGLViewer import OpenGLViewer


class VideoApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        # init external object
        self.synchObject = SynchObject(60)
        self.input1 = RandomNoiseGenerator(self.synchObject)
        # init internal widget
        self.widget = QWidget()
        self.viewer = OpenGLViewer()
        self.fpsLabel = QLabel("FPS: 0.00")  # Initialize FPS label
        self.displayLabel = QLabel()
        self.uiTimer = QTimer(self)
        self.uiTimer.start(1000 // 30)  # Update UI at 30 FPS
        self.btnApplyClahe = QPushButton("Apply CLAHE")
        self.btnApplyHistogramEqualization = QPushButton("Apply Histogram Equalization")
        self.btnApplyGammaCorrection = QPushButton("Apply Gamma Correction")
        self.btnApplyInvert = QPushButton("invert")
        self.qImage = QImage()
        # init the interface
        self.initUI()
        self.initConnections()
        self.initGeometry()
        # test the payload
        #self.testPayload()

    def initUI(self):
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.viewer)
        mainLayout.addWidget(self.fpsLabel)
        mainLayout.addWidget(self.displayLabel)
        buttonLayout = self.initButtonLayout()
        mainLayout.addLayout(buttonLayout)
        self.widget.setLayout(mainLayout)

    def initButtonLayout(self):
        self.initButton(self.btnApplyClahe, self.setClahe)
        self.initButton(self.btnApplyHistogramEqualization, self.setHistogramEqualization)
        self.initButton(self.btnApplyGammaCorrection, self.setGammaCorrection)
        self.initButton(self.btnApplyInvert, self.setInvert)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.btnApplyClahe)
        buttonLayout.addWidget(self.btnApplyHistogramEqualization)
        buttonLayout.addWidget(self.btnApplyGammaCorrection)
        buttonLayout.addWidget(self.btnApplyInvert)
        return buttonLayout

    def initButton(self, button, function):
        button.setCheckable(True)
        button.setChecked(False)
        button.clicked.connect(function)

    def initConnections(self):
        self.uiTimer.timeout.connect(self.display_frame)
        #QTimer.singleShot(10000, self.stop_app)

    def initGeometry(self):
        self.viewer.setFixedSize(1920, 1080)
        #self.widget.setGeometry(10, 50, 1920, 1080)
        self.widget.show()

    def testPayload(self):
        print("Payload test")
        #self.input1.isFlipped = True
        self.input1.isFrameInverted = True
        self.input1.isFrameAutoScreen = True
        self.input1.isFrameHistogramEqualizationYUV = True

    def display_frame(self):
        frame = self.input1.getFrame()
        if frame is not None and frame.size != 0:
            start_time = time.time()
            self.qImage = QImage(frame.data, frame.shape[1], frame.shape[0],
                                 QImage.Format.Format_BGR888)
            self.viewer.setImage(self.qImage)
            display_time = time.time() - start_time
            self.displayLabel.setText(f"Frame displayed in {display_time:.6f} seconds")
            self.fpsLabel.setText(f"FPS: {self.input1.fps:.2f}")  # Update FPS label

    def stop_app(self):
        print(f"Media FPS: {self.input1.fps:.2f}")
        self.exit()

    def setClahe(self):
        self.input1.isFrameClahe = self.btnApplyClahe.isChecked()

    def setHistogramEqualization(self):
        self.input1.isFrameHistogramEqualizationYUV = self.btnApplyHistogramEqualization.isChecked()

    def setGammaCorrection(self):
        self.input1.isFrameGammaCorrection = self.btnApplyGammaCorrection.isChecked()

    def setInvert(self):
        self.input1.isFrameInverted = self.btnApplyInvert.isChecked()


if __name__ == "__main__":
    import sys
    import cProfile
    import pstats
    import io


    def main():
        app = VideoApp(sys.argv)
        app.exec()


    pr = cProfile.Profile()
    pr.enable()
    main()
    pr.disable()
    s = io.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())
