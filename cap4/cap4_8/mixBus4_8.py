import os
from enum import Enum

import cv2
import numpy as np
from PyQt6.QtCore import *


class MIX_TYPE(Enum):
    FADE = 0
    WIPE_LEFT_TO_RIGHT = 1
    WIPE_RIGHT_TO_LEFT = 2
    WIPE_TOP_TO_BOTTOM = 3
    WIPE_BOTTOM_TO_TOP = 4
    WIPE_STINGER = 5


class MixBus4_8(QObject):
    _fade = 0
    fadeTime = 100
    _wipe = 0
    _wipeTime = 90
    effectType = MIX_TYPE.WIPE_STINGER
    stinger_frames = []
    stinger_invMasks = []

    def __init__(self, input1, input2, loaderThread, parent=None):
        super().__init__(parent)
        self.previewInput = input1
        self.programInput = input2
        self.autoMix_timer = QTimer(self)
        self.autoMix_timer.timeout.connect(self._fader)
        self._init_wipe_positions()
        self.setStinger(loaderThread)

    def _init_wipe_positions(self):
        _wipe_step = max(1, self._wipeTime)
        self._wipe_position_leftToRight_list = np.linspace(0, 1920, _wipe_step)
        self._wipe_position_rightToLeft_list = np.linspace(1920, 0, _wipe_step)
        self._wipe_position_topToBottom_list = np.linspace(0, 1080, _wipe_step)
        self._wipe_position_bottomToTop_list = np.linspace(1080, 0, _wipe_step)

    def setStinger(self, loaderThread):
        self.loaderThread = loaderThread
        self.stinger_frames = []
        self.stinger_invMasks = []
        loaderThread.stingerReady.connect(self.onStingerReady)
        loaderThread.start()

    @pyqtSlot()
    def onStingerReady(self):
        self.stinger_frames = self.loaderThread.stingerPreMultipliedImages
        self.stinger_invMasks = self.loaderThread.stingerInvAlphaImages

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
            elif self.effectType == MIX_TYPE.WIPE_RIGHT_TO_LEFT:
                return prw_frame, self.wipeRightToLeft(prw_frame, prg_frame)
            elif self.effectType == MIX_TYPE.WIPE_TOP_TO_BOTTOM:
                return prw_frame, self.wipeTopToBottom(prw_frame, prg_frame)
            elif self.effectType == MIX_TYPE.WIPE_BOTTOM_TO_TOP:
                return prw_frame, self.wipeBottomToTop(prw_frame, prg_frame)
            elif self.effectType == MIX_TYPE.WIPE_STINGER:
                return prw_frame, self.stinger(prw_frame, prg_frame)

    def setFade(self, value: int):
        if value == 0:
            self._fade = 0
        else:
            self._fade = value / 100
            self._wipe = value

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
        elif self.effectType in [MIX_TYPE.WIPE_LEFT_TO_RIGHT, MIX_TYPE.WIPE_RIGHT_TO_LEFT,
                                 MIX_TYPE.WIPE_TOP_TO_BOTTOM, MIX_TYPE.WIPE_BOTTOM_TO_TOP]:
            self._wipe += 1
            self._fade += 0.01
            if self._wipe > len(self._wipe_position_leftToRight_list) - 1:
                self.autoMix_timer.stop()
                self.cut()
        elif self.effectType == MIX_TYPE.WIPE_STINGER:
            self._wipe += 1
            self._fade += 0.01
            if self._wipe > len(self.stinger_frames) - 1:
                self.autoMix_timer.stop()
                self.cut()

    def wipeLeftToRight(self, preview_frame, program_frame):
        wipe_position = int(self._wipe_position_leftToRight_list[self._wipe])
        wipe_frame = program_frame.copy()
        wipe_frame[:, :wipe_position] = preview_frame[:, :wipe_position]
        return wipe_frame

    def wipeRightToLeft(self, preview_frame, program_frame):
        wipe_position = int(self._wipe_position_rightToLeft_list[self._wipe])
        wipe_frame = program_frame.copy()
        wipe_frame[:, wipe_position:] = preview_frame[:, wipe_position:]
        return wipe_frame

    def wipeTopToBottom(self, preview_frame, program_frame):
        wipe_position = int(self._wipe_position_topToBottom_list[self._wipe])
        wipe_frame = program_frame.copy()
        wipe_frame[:wipe_position, :] = preview_frame[:wipe_position, :]
        return wipe_frame

    def wipeBottomToTop(self, preview_frame, program_frame):
        wipe_position = int(self._wipe_position_bottomToTop_list[self._wipe])
        wipe_frame = program_frame.copy()
        wipe_frame[wipe_position:, :] = preview_frame[wipe_position:, :]
        return wipe_frame

    def stinger(self, preview_frame, program_frame):
        stinger_frame = self.stinger_frames[self._wipe]
        inv_mask = self.stinger_invMasks[self._wipe]

        if self._wipe < len(self.stinger_frames) // 2:
            program_masked = cv2.multiply(program_frame, inv_mask, dtype=cv2.CV_8U)
            result = cv2.add(stinger_frame, program_masked)
            return np.ascontiguousarray(result)
        else:
            preview_masked = cv2.multiply(preview_frame, inv_mask, dtype=cv2.CV_8U)
            result = cv2.add(stinger_frame, preview_masked)
            return np.ascontiguousarray(result)
