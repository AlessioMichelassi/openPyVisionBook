import os
import time
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
    FADE_STILL = 6


class MixBusMain(QObject):
    _fade = 0
    fadeTime = 100
    _wipe = 0
    _wipeTime = 90
    effectType = MIX_TYPE.FADE
    stinger_frames = []
    stinger_invMasks = []
    isStingerLoaded = False
    isStillLoaded = False
    still = None

    _wipe_position_leftToRight_list = []
    _wipe_position_rightToLeft_list = []
    _wipe_position_topToBottom_list = []
    _wipe_position_bottomToTop_list = []
    _wipe_position_stinger_list = []

    def __init__(self, input1, input2, parent=None):
        super().__init__(parent)
        self.previewInput = input1
        self.programInput = input2
        self.autoMix_timer = QTimer(self)
        self.autoMix_timer.timeout.connect(self._fader)
        self._init_wipe_positions()
        # Variabili per il calcolo del frame rate
        self.total_frames = 0
        self.total_time = 0
        self.start_time = time.time()
        self.last_fps = 0

    def _init_wipe_positions(self):
        """
        This function initializes the wipe positions based on the wipe time.
        :return:
        """
        _wipe_step = max(1, self._wipeTime)
        self._wipe_position_leftToRight_list = np.linspace(0, 1920, _wipe_step)
        self._wipe_position_rightToLeft_list = np.linspace(1920, 0, _wipe_step)
        self._wipe_position_topToBottom_list = np.linspace(0, 1080, _wipe_step)
        self._wipe_position_bottomToTop_list = np.linspace(1080, 0, _wipe_step)
        self._wipe_position_stinger_list = []

    def setStinger(self, stingerObject):
        """
        This function sets the stinger frames and the stinger inv masks.
        :param stingerObject:
        :return:
        """
        self.stinger_frames = stingerObject.stingerPreMultipliedImages
        self.stinger_invMasks = stingerObject.stingerInvAlphaImages
        self.isStingerLoaded = True
        _wipe_step = max(1, self._wipeTime)
        self._wipe_position_stinger_list = np.linspace(0, len(self.stinger_frames) - 1, _wipe_step)

    def setStill(self, stillObject):
        """
        This function sets the still image.
        :param stillObject:
        :return:
        """
        self.still = stillObject
        self.isStillLoaded = True

    def getMixed(self):
        """
        This function returns the mixed frame based on the effect type.
        I talk about how to create a mix bus in the 4.1 - Mix Bus
            you can find it at:
            https://github.com/AlessioMichelassi/openPyVision_013/wiki/Chapter-4
        :return:
        """
        prw_frame = self.previewInput.getFrame()
        prg_frame = self.programInput.getFrame()

        # This updates the frame rate
        self.total_frames += 1
        self.total_time += time.time() - self.start_time
        self.start_time = time.time()

        # calculate the frame rate measured in frames per second
        if self.total_time > 0:
            self.last_fps = self.total_frames / self.total_time

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
                if not self.isStingerLoaded:
                    return prw_frame, prg_frame
                return prw_frame, self.stinger(prw_frame, prg_frame)
            elif self.effectType == MIX_TYPE.FADE_STILL:
                if not self.isStillLoaded:
                    print("Still not loaded")
                    return prw_frame, prg_frame
                return prw_frame, cv2.addWeighted(self.still.getFrame(), self._fade, prg_frame, 1 - self._fade, 0)

    def get_fps(self):
        """
        Return the current FPS during mixing.
        """
        return self.last_fps

    def setFade(self, value: int):
        """
        This function sets the fade value. It also maps the slider value (0-100)
        to the appropriate index for the wipe or stinger effect.
        :param value: Value from the slider (0-100)
        :return:
        """
        if value == 0:
            self._fade = 0
        else:
            self._fade = value / 100

            if self.effectType == MIX_TYPE.WIPE_LEFT_TO_RIGHT:
                self._wipe = self.map_value(value, 0, 100, 0, len(self._wipe_position_leftToRight_list) - 1)
            elif self.effectType == MIX_TYPE.WIPE_RIGHT_TO_LEFT:
                self._wipe = self.map_value(value, 0, 100, 0, len(self._wipe_position_rightToLeft_list) - 1)
            elif self.effectType == MIX_TYPE.WIPE_TOP_TO_BOTTOM:
                self._wipe = self.map_value(value, 0, 100, 0, len(self._wipe_position_topToBottom_list) - 1)
            elif self.effectType == MIX_TYPE.WIPE_BOTTOM_TO_TOP:
                self._wipe = self.map_value(value, 0, 100, 0, len(self._wipe_position_bottomToTop_list) - 1)
            elif self.effectType == MIX_TYPE.WIPE_STINGER and self.isStingerLoaded:
                self._wipe = self.map_value(value, 0, 100, 0, len(self._wipe_position_stinger_list) - 1)

    @staticmethod
    def map_value(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def cut(self):
        """
        This function swaps the preview and program inputs.
        :return:
        """
        self._fade = 0
        self._wipe = 0
        self.previewInput, self.programInput = self.programInput, self.previewInput

    def autoMix(self):
        """
        This function starts the timer that will update the fade value.
        :return:
        """
        self.autoMix_timer.start(1000 // 60)

    def _fader(self):
        """
        This function updates the fade value based on the effect type.
        :return:
        """
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
        elif self.effectType == MIX_TYPE.FADE_STILL:
            self._fade += 0.01
            if self._fade > 1:
                self.autoMix_timer.stop()

    def wipeLeftToRight(self, preview_frame, program_frame):
        """
            This function creates a wipe effect from left to right.
            I talk about how to create a wipe effect in the 4.2 - Wipe Left To Right
            you can find it at:
            https://github.com/AlessioMichelassi/openPyVision_013/wiki/Chapter-4
        :param preview_frame: the preview frame from input 1
        :param program_frame: the program frame from input 2
        :return: the frame with the wipe effect
        """
        wipe_position = int(self._wipe_position_leftToRight_list[self._wipe])
        wipe_frame = program_frame.copy()
        wipe_frame[:, :wipe_position] = preview_frame[:, :wipe_position]
        return wipe_frame

    def wipeRightToLeft(self, preview_frame, program_frame):
        """
            This function creates a wipe effect from left to right.
            I talk about how to create a wipe effect in the 4.3 - Wipe Right To Left
            you can find it at:
            https://github.com/AlessioMichelassi/openPyVision_013/wiki/Chapter-4
        :param preview_frame: the preview frame from input 1
        :param program_frame: the program frame from input 2
        :return: the frame with the wipe effect
        """
        wipe_position = int(self._wipe_position_rightToLeft_list[self._wipe])
        wipe_frame = program_frame.copy()
        wipe_frame[:, wipe_position:] = preview_frame[:, wipe_position:]
        return wipe_frame

    def wipeTopToBottom(self, preview_frame, program_frame):
        """
            This function creates a wipe effect from left to right.
            I talk about how to create a wipe effect in the 4.4 - Wipe Up And Down
            you can find it at:
            https://github.com/AlessioMichelassi/openPyVision_013/wiki/Chapter-4
        :param preview_frame: the preview frame from input 1
        :param program_frame: the program frame from input 2
        :return: the frame with the wipe effect
        """
        wipe_position = int(self._wipe_position_topToBottom_list[self._wipe])
        wipe_frame = program_frame.copy()
        wipe_frame[:wipe_position, :] = preview_frame[:wipe_position, :]
        return wipe_frame

    def wipeBottomToTop(self, preview_frame, program_frame):
        """
            This function creates a wipe effect from left to right.
            I talk about how to create a wipe effect in the 4.4 - Wipe Up And Down
            you can find it at:
            https://github.com/AlessioMichelassi/openPyVision_013/wiki/Chapter-4
        :param preview_frame: the preview frame from input 1
        :param program_frame: the program frame from input 2
        :return: the frame with the wipe effect
        """
        wipe_position = int(self._wipe_position_bottomToTop_list[self._wipe])
        wipe_frame = program_frame.copy()
        wipe_frame[wipe_position:, :] = preview_frame[wipe_position:, :]
        return wipe_frame

    def stinger(self, preview_frame, program_frame):
        """
        This function creates a stinger effect.
        I talk about how to create a stinger effect in the 4.5 - Stinger
            you can find it at:
            https://github.com/AlessioMichelassi/openPyVision_013/wiki/Chapter-4
        :param preview_frame:
        :param program_frame:
        :return:
        """
        _wipePosition = int(self._wipe_position_stinger_list[self._wipe])
        stinger_frame = self.stinger_frames[_wipePosition]
        inv_mask = self.stinger_invMasks[_wipePosition]

        if self._wipe < len(self.stinger_frames) // 2:
            program_masked = cv2.multiply(program_frame, inv_mask, dtype=cv2.CV_8U)
            result = cv2.add(stinger_frame, program_masked)
            return np.ascontiguousarray(result)
        else:
            preview_masked = cv2.multiply(preview_frame, inv_mask, dtype=cv2.CV_8U)
            result = cv2.add(stinger_frame, preview_masked)
            return np.ascontiguousarray(result)
