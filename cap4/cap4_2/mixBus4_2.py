import time
from enum import Enum

import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class MIX_TYPE(Enum):
    FADE = 0
    WIPE_LEFT_TO_RIGHT = 1
    WIPE_RIGHT_TO_LEFT = 2
    WIPE_TOP_TO_BOTTOM = 3
    WIPE_BOTTOM_TO_TOP = 4


class MixBus4_2(QObject):
    _fade = 0
    fadeTime = 100
    _wipe = 0
    _wipeTime = 100
    effectType = MIX_TYPE.WIPE_LEFT_TO_RIGHT

    def __init__(self, input1, input2, parent=None):
        super().__init__(parent)
        self.previewInput = input1
        self.programInput = input2
        self.autoMix_timer = QTimer(self)
        self.autoMix_timer.timeout.connect(self._fader)
        self._init_wipe_positions()

    def _init_wipe_positions(self):
        _wipe_step = max(1, self._wipeTime)
        self._wipe_position_list = np.linspace(0, 1920, _wipe_step)

    def getMixed(self):
        prw_frame = self.previewInput.getFrame()
        prg_frame = self.programInput.getFrame()
        if self._fade == 0:
            return prw_frame, prg_frame
        else:
            if self.effectType == MIX_TYPE.FADE:
                return prw_frame, cv2.addWeighted(prw_frame, self._fade, prg_frame, 1 - self._fade, 0)
            elif self.effectType == MIX_TYPE.WIPE_LEFT_TO_RIGHT:
                return prw_frame, self.wipeLeftToRight(prw_frame, prg_frame)

    def setFade(self, value: int):
        if value == 0:
            self._fade = 0
            self._wipe = 0
        else:
            self._fade = value / 100
            self._wipe = value - 1
        print(f"Fade: {self._fade}, Wipe: {self._wipe} - {self._wipe_position_list[self._wipe]}")

    def cut(self):
        self._fade = 0
        self._wipe = 0
        self.previewInput, self.programInput = self.programInput, self.previewInput

    def autoMix(self):
        self.autoMix_timer.start(1000 // 60)

    def _fader(self):
        if self.effectType == MIX_TYPE.FADE:
            self._fade += 0.01
            if self._fade > 1:
                self.autoMix_timer.stop()
                self.cut()
        elif self.effectType == MIX_TYPE.WIPE_LEFT_TO_RIGHT:
            self._wipe += 1
            self._fade += 0.01
            if self._wipe > len(self._wipe_position_list) - 1:
                self.autoMix_timer.stop()
                self.cut()

    def wipeLeftToRight(self, preview_frame, program_frame):
        wipe_position = int(self._wipe_position_list[self._wipe])
        wipe_frame = program_frame.copy()
        wipe_frame[:, :wipe_position] = preview_frame[:, :wipe_position]
        return wipe_frame
