import time
import logging
from enum import Enum

import cv2
import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QTimer, QThreadPool, QMutex, QMutexLocker, QMetaObject, Qt, \
    Q_ARG, pyqtSlot

# Configure logging
logging.basicConfig(level=logging.INFO)


class MIX_TYPE(Enum):
    """
    Enumeration of available mixing effects.
    """
    FADE = 0
    WIPE_LEFT_TO_RIGHT = 1
    WIPE_RIGHT_TO_LEFT = 2
    WIPE_TOP_TO_BOTTOM = 3
    WIPE_BOTTOM_TO_TOP = 4
    WIPE_STINGER1 = 5
    WIPE_STINGER2 = 6
    FADE_STILL1 = 7
    FADE_STILL2 = 8
    FADE_STILL3 = 9
    FADE_STILL4 = 10


class MixBusWorker(QRunnable):
    """
    Worker class for mixing two video frames using a specified effect.
    This class runs in a separate thread.
    """

    def __init__(self, prw_frame, prg_frame, fade, wipe, effect_type, stills, stingers, wipe_positions, callback):
        """
        Initialize the MixBusWorker.

        :param prw_frame: The preview frame (numpy array).
        :param prg_frame: The program frame (numpy array).
        :param fade: The fade value (float between 0 and 1).
        :param wipe: The wipe position index (int).
        :param effect_type: The type of mixing effect (MIX_TYPE enum).
        :param stills: Dictionary of still images.
        :param stingers: Dictionary of stinger animations.
        :param wipe_positions: Dictionary with wipe positions arrays.
        :param callback: Callback function to return the mixed frame.
        """
        super().__init__()
        self.prw_frame = prw_frame
        self.prg_frame = prg_frame
        self.fade = fade
        self.wipe = wipe
        self.effect_type = effect_type
        self.stills = stills
        self.stingers = stingers
        self.wipe_positions = wipe_positions
        self.callback = callback  # Callback to return the mixed frame

    def run(self):
        """
        Mixing logic executed in a separate thread.
        """
        try:
            if self.prw_frame is None or self.prg_frame is None:
                logging.warning("One of the frames is None.")
                return

            if self.prw_frame.shape != self.prg_frame.shape:
                logging.warning("Frames have different dimensions.")
                return

            mixed_frame = self.prg_frame.copy()

            if self.effect_type == MIX_TYPE.FADE:
                mixed_frame = cv2.addWeighted(self.prw_frame, self.fade, self.prg_frame, 1 - self.fade, 0)
            elif self.effect_type == MIX_TYPE.WIPE_LEFT_TO_RIGHT:
                mixed_frame = self.wipeLeftToRight(self.prw_frame, self.prg_frame)
            elif self.effect_type == MIX_TYPE.WIPE_RIGHT_TO_LEFT:
                mixed_frame = self.wipeRightToLeft(self.prw_frame, self.prg_frame)
            # Add other effects as needed
            else:
                logging.warning(f"Effect type {self.effect_type} not implemented.")

            self.callback(mixed_frame)  # Return the mixed frame via callback
        except Exception as e:
            logging.exception(f"Exception in MixBusWorker: {e}")

    def wipeLeftToRight(self, preview_frame, program_frame):
        """
        Perform a left-to-right wipe transition between preview and program frames.

        :param preview_frame: The preview frame.
        :param program_frame: The program frame.
        :return: The mixed frame after applying the wipe effect.
        """
        wipe_position = int(self.wipe_positions["leftToRight"][int(self.wipe)])
        wipe_frame = program_frame.copy()
        wipe_frame[:, :wipe_position] = preview_frame[:, :wipe_position]
        return wipe_frame

    def wipeRightToLeft(self, preview_frame, program_frame):
        """
        Perform a right-to-left wipe transition between preview and program frames.

        :param preview_frame: The preview frame.
        :param program_frame: The program frame.
        :return: The mixed frame after applying the wipe effect.
        """
        wipe_position = int(self.wipe_positions["rightToLeft"][int(self.wipe)])
        wipe_frame = program_frame.copy()
        wipe_frame[:, wipe_position:] = preview_frame[:, wipe_position:]
        return wipe_frame


class MixBus016(QObject):
    """
    MixBus class responsible for mixing two video inputs based on tally commands.
    """
    frame_ready = pyqtSignal(np.ndarray, np.ndarray, float)  # Signal to emit frames and FPS

    def __init__(self, videoHub):
        """
        Initialize the MixBus.

        :param videoHub: The VideoHubData instance containing input devices.
        """
        super().__init__()
        self.videoHub = videoHub
        self.previewInput = self.videoHub.getInputDevice(1)
        self.programInput = self.videoHub.getInputDevice(2)
        self._fade = 0
        self._wipe = 0
        self._wipeTime = 90  # Duration of the wipe effect
        self.effect_type = MIX_TYPE.FADE
        self.stills = {}
        self.stingers = {}
        self.isStingerLoaded = {1: False, 2: False}
        self.isStillLoaded = {1: False, 2: False, 3: False, 4: False}
        self.still = None
        self.actualPreviewIndex = 1
        self.actualProgramIndex = 2
        self._wipe_position_leftToRight_list = np.linspace(0, 1920, self._wipeTime)
        self._wipe_position_rightToLeft_list = np.linspace(1920, 0, self._wipeTime)
        self.thread_pool = QThreadPool.globalInstance()  # Use global thread pool
        self.total_frames = 0
        self.total_time = 0
        self.start_time = time.time()
        self.last_fps = 60
        self.input_mutex = QMutex()  # Mutex for thread-safe access to inputs

        # Timer for automix
        self.autoMix_timer = QTimer(self)
        self.autoMix_timer.timeout.connect(self._fader)

    def getMixed(self):
        """
        Initiate the mixing process.
        """
        start_time = time.perf_counter()
        with QMutexLocker(self.input_mutex):
            prw_input = self.previewInput
            prg_input = self.programInput

        prw_frame = prw_input.getFrame() if prw_input else None
        prg_frame = prg_input.getFrame() if prg_input else None

        # Calculate FPS
        current_time = time.time()
        self.total_frames += 1
        self.total_time += current_time - self.start_time
        self.start_time = current_time
        if self.total_time > 0:
            self.last_fps = self.total_frames / self.total_time

        # Create a worker to process the frames
        worker = MixBusWorker(
            prw_frame, prg_frame, self._fade, self._wipe, self.effect_type,
            self.stills, self.stingers, self.getWipePositions(), self.handle_frame_processed
        )

        # Execute the worker in the thread pool
        self.thread_pool.start(worker)
        end_time = time.perf_counter()
        processing_time = (end_time - start_time) * 1000  # Tempo in millisecondi
        # logging.debug(f"MixBus.getMixed() took {processing_time:.2f} ms")

    def handle_frame_processed(self, mixed_frame):
        """
        Handle the mixed frame processed by the worker.

        :param mixed_frame: The mixed frame result from the worker.
        """
        # Emit the frame_ready signal in the main thread
        QMetaObject.invokeMethod(
            self, "emit_frame_ready", Qt.ConnectionType.QueuedConnection,
            Q_ARG(np.ndarray, self.previewInput.getFrame()),
            Q_ARG(np.ndarray, mixed_frame),
            Q_ARG(float, self.last_fps)
        )

    @pyqtSlot(np.ndarray, np.ndarray, float)
    def emit_frame_ready(self, prw_frame, prg_frame, fps):
        """
        Emit the frame_ready signal with the provided frames and FPS.

        :param prw_frame: The preview frame.
        :param prg_frame: The program (mixed) frame.
        :param fps: The calculated frames per second.
        """
        self.frame_ready.emit(prw_frame, prg_frame, fps)

    def setFade(self, value: int):
        """
        Set the fade value and update wipe positions accordingly.

        :param value: Fade value between 0 and 100.
        """
        with QMutexLocker(self.input_mutex):
            if value == 0:
                self._fade = 0
            else:
                self._fade = value / 100

                if self.effect_type == MIX_TYPE.WIPE_LEFT_TO_RIGHT:
                    self._wipe = self.map_value(value, 0, 100, 0, len(self._wipe_position_leftToRight_list) - 1)
                elif self.effect_type == MIX_TYPE.WIPE_RIGHT_TO_LEFT:
                    self._wipe = self.map_value(value, 0, 100, 0, len(self._wipe_position_rightToLeft_list) - 1)

    def getWipePositions(self):
        """
        Get the positions for wipe effects.

        :return: Dictionary containing wipe positions for left-to-right and right-to-left wipes.
        """
        return {
            "leftToRight": self._wipe_position_leftToRight_list,
            "rightToLeft": self._wipe_position_rightToLeft_list
        }

    def setEffectType(self, effect_type):
        """
        Set the mixing effect type.

        :param effect_type: The effect type from MIX_TYPE enum.
        """
        with QMutexLocker(self.input_mutex):
            self.effect_type = effect_type

    def setStill(self, position, still_frame):
        """
        Set a still image at the specified position.

        :param position: Position index for the still image.
        :param still_frame: The still image frame.
        """
        self.stills[position] = still_frame

    def setStinger(self, position, stinger_frame, inv_mask):
        """
        Set a stinger animation at the specified position.

        :param position: Position index for the stinger.
        :param stinger_frame: The stinger frame.
        :param inv_mask: The inverse mask for the stinger.
        """
        self.stingers[position] = (stinger_frame, inv_mask)

    def cut(self):
        """
        Perform an immediate cut between preview and program inputs.
        """
        with QMutexLocker(self.input_mutex):
            self._fade = 0
            self._wipe = 0
            self.previewInput, self.programInput = self.programInput, self.previewInput

    def autoMix(self):
        """
        Start the automix transition.
        """
        logging.info(f"Starting AutoMix for duration {self._wipeTime}")
        self.autoMix_timer.start(1000 // 60)  # Adjust timer interval as needed

    def _fader(self):
        """
        Internal method to handle fade and wipe transitions over time.
        """
        if self.effect_type == MIX_TYPE.FADE:
            self._fade += 0.01
            if self._fade >= 1:
                self.autoMix_timer.stop()
                self.cut()
        elif self.effect_type in [MIX_TYPE.WIPE_LEFT_TO_RIGHT, MIX_TYPE.WIPE_RIGHT_TO_LEFT]:
            self._wipe += 1
            self._fade += 0.01
            if self._wipe >= len(self._wipe_position_leftToRight_list) - 1:
                self.autoMix_timer.stop()
                self.cut()

    def getTally(self, tally_data):
        """
        Update MixBus state based on data received from the TallyManager.

        :param tally_data: Dictionary containing tally commands and data.
        """
        logging.debug(f"MixBus received tally data: {tally_data}")
        tally_data['sender'] = 'mixBus'
        cmd = tally_data.get('cmd')
        if cmd == 'cut':
            self.cut()
        elif cmd == 'auto':
            logging.info(f"AutoMix command received.")
            self.autoMix()
        elif cmd == 'faderChange':
            fade_value = int(float(tally_data.get('fade', 0)) * 100)
            self.setFade(fade_value)
        elif cmd == 'effectChange':
            effect = tally_data.get('effect')
            effect_enum = getattr(MIX_TYPE, effect.replace(" ", "_").upper(), MIX_TYPE.FADE)
            self.setEffectType(effect_enum)
            logging.info(f"Effect changed to {effect_enum}")
        elif cmd == 'previewChange':
            logging.info(f"Preview input change to {tally_data['preview']}")
            self.actualPreviewIndex = int(tally_data['preview'])
            new_preview_input = self.videoHub.getInputDevice(self.actualPreviewIndex)
            with QMutexLocker(self.input_mutex):
                self.previewInput = new_preview_input
        elif cmd == 'programChange':
            logging.info(f"Program input change to {tally_data['program']}")
            self.actualProgramIndex = int(tally_data['program'])
            new_program_input = self.videoHub.getInputDevice(self.actualProgramIndex)
            with QMutexLocker(self.input_mutex):
                self.programInput = new_program_input
        elif cmd == 'inputChanged':
            position = tally_data.get('position')
            if position == self.actualPreviewIndex:
                with QMutexLocker(self.input_mutex):
                    self.previewInput = self.videoHub.getInputDevice(position)
            elif position == self.actualProgramIndex:
                with QMutexLocker(self.input_mutex):
                    self.programInput = self.videoHub.getInputDevice(position)
        elif cmd == 'stingerReady':
            position = tally_data.get('position')
            stingerObject = self.videoHub.getStinger(position)
            if stingerObject:
                self.setStinger(position, *stingerObject)
                self.isStingerLoaded[position] = True
        elif cmd == 'stillImageReady':
            position = tally_data.get('position')
            stillImage = self.videoHub.getStillImage(position)
            if stillImage:
                self.setStill(position, stillImage)
                self.isStillLoaded[position] = True
        else:
            logging.warning(f"Unknown command received in getTally: {cmd}")

    def map_value(self, x, in_min, in_max, out_min, out_max):
        """
        Map a value from one range to another.

        :param x: The input value.
        :param in_min: Minimum of input range.
        :param in_max: Maximum of input range.
        :param out_min: Minimum of output range.
        :param out_max: Maximum of output range.
        :return: The mapped value.
        """
        return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

    def stop(self):
        """
        Stop the MixBus processing and timers.
        """
        self.autoMix_timer.stop()
        # Wait for all threads in the thread pool to finish
        self.thread_pool.waitForDone()
        logging.info("MixBus stopped.")
