import cv2
from PyQt6.QtCore import *


class MixBus4_1(QObject):
    _fade = 0
    fadeTime = 100

    def __init__(self, input1, input2, parent=None):
        super().__init__(parent)
        self.previewInput = input1
        self.programInput = input2
        self.autoMix_timer = QTimer(self)
        self.autoMix_timer.timeout.connect(self._fadeTo)

    def getMixed(self):
        prw_frame = self.previewInput.getFrame()
        prg_frame = self.programInput.getFrame()
        if self._fade == 0:
            return prw_frame, prg_frame
        else:
            return prw_frame, cv2.addWeighted(prw_frame, self._fade, prg_frame, 1 - self._fade, 0)

    def cut(self):
        self._fade = 0
        self.previewInput, self.programInput = self.programInput, self.previewInput

    def autoMix(self):
        self.autoMix_timer.start(self.fadeTime)

    def _fadeTo(self):
        self._fade += 0.1
        if self._fade > 1:
            self.autoMix_timer.stop()
            self.cut()

    def setFade(self, value: int):
        if value == 0:
            self._fade = 0
        else:
            self._fade = value/100


