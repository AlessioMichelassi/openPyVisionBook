import sys
import time
from enum import Enum

import cv2
import numpy as np
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import *
from functools import partial
from cap5.mainDir.data.dataManager import DataManager
from cap5.mainDir.inputs.colorGenerator import ColorGenerator
from cap5.mainDir.inputs.randomNoiseGenerator import RandomNoiseGenerator


class LblWidget(QLineEdit):
    lblStyle = """
                QLineEdit {
                    background-color: rgb(20, 20, 25);
                    border: 1px solid rgb(0, 0, 80);
                    border-radius: 5px;
                    color: rgb(153, 204, 255);
                    font-weight: bold;
                    font-size: 12px;
                }
                """

    def __init__(self, name, index, size, parent=None):
        super().__init__(parent)
        if name == "Input":
            self.name = f"Input_{index}"
            self.setText(self.name)
        else:
            self.name = name
            self.setText(self.name)
        self.setObjectName(f"lblInput_{index}")
        self.setBaseSize(QSize(size[0], size[1]))
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(self.lblStyle)
        self.setReadOnly(True)
        self.returnPressed.connect(self.onReturnPressed)  # Connect the returnPressed signal to the method

    def mouseDoubleClickEvent(self, event):
        self.setReadOnly(False)

    def focusOutEvent(self, event):
        self.setReadOnly(True)
        self.setObjectName(self.text())  # Update the object name when focus is lost

    def onReturnPressed(self):
        self.setObjectName(self.text())
        self.name = self.text()
        self.setReadOnly(True)


class SynchObject(QObject):
    synch_SIGNAL = pyqtSignal()

    def __init__(self, fps=60, parent=None):  # Set FPS to 60
        super().__init__(parent)
        self.fps = fps
        self.syncTimer = QTimer(self)
        self.syncTimer.timeout.connect(self.sync)
        self.syncTimer.start(1000 // fps)
        self._initialized = True

    def sync(self):
        self.synch_SIGNAL.emit()


class MIX_TYPE(Enum):
    FADE = 0
    WIPE_LEFT_TO_RIGHT = 1
    WIPE_RIGHT_TO_LEFT = 2
    WIPE_TOP_TO_BOTTOM = 3
    WIPE_BOTTOM_TO_TOP = 4
    WIPE_STINGER = 5
    FADE_STILL = 6


class MixBus015T(QObject):
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

    # Signal to send the mixed frame back to the main thread
    mixed_frame_ready_SIGNAL = pyqtSignal(np.ndarray, np.ndarray)
    fps_updated_SIGNAL = pyqtSignal(float)

    _running = False

    def __init__(self, input1, input2, crossBar=None, parent=None):
        super().__init__(parent)
        self.previewInput = input1
        self.programInput = input2
        self.crossBar = crossBar
        self.autoMix_timer = QTimer(self)
        self.autoMix_timer.timeout.connect(self._fader)
        self._init_wipe_positions()
        # Variabili per il calcolo del frame rate
        self.total_frames = 0
        self.total_time = 0
        self.start_time = time.time()
        self.last_fps = 0
        # Thread
        self.thread = QThread()

    def _init_wipe_positions(self):
        # Inizializzazione delle posizioni per il wipe
        _wipe_step = max(1, self._wipeTime)
        self._wipe_position_leftToRight_list = np.linspace(0, 1920, _wipe_step)
        self._wipe_position_rightToLeft_list = np.linspace(1920, 0, _wipe_step)
        self._wipe_position_topToBottom_list = np.linspace(0, 1080, _wipe_step)
        self._wipe_position_bottomToTop_list = np.linspace(1080, 0, _wipe_step)
        self._wipe_position_stinger_list = []

    def setStinger(self, stingerObject):
        self.stinger_frames = stingerObject.stingerPreMultipliedImages
        self.stinger_invMasks = stingerObject.stingerInvAlphaImages
        self.isStingerLoaded = True
        _wipe_step = max(1, self._wipeTime)
        self._wipe_position_stinger_list = np.linspace(0, len(self.stinger_frames) - 1, _wipe_step)

    def setStill(self, stillObject):
        self.still = stillObject
        self.isStillLoaded = True

    def processMix(self):
        while self._running:
            mixed_preview, mixed_program = self.getMixed()
            self.mixed_frame_ready_SIGNAL.emit(mixed_preview, mixed_program)
            QThread.msleep(15)  # Simula un frame rate di circa 60 FPS

    def startProcessing(self):
        self._running = True
        self.moveToThread(self.thread)
        self.thread.started.connect(self.processMix)
        self.thread.start()

    def stop(self):
        self._running = False
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

    def getMixed(self):
        """
        Questa funzione restituisce il frame mixato in base all'effetto e al fade impostati.
        NON E' LA FUNZIONE CHIAMATA DAL THREAD
        :return:
        """
        prw_frame = self.previewInput.getFrame()
        prg_frame = self.programInput.getFrame()

        self.total_frames += 1
        self.total_time += time.time() - self.start_time
        self.start_time = time.time()

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

    def runMixThread(self):
        while self._running:
            prw_frame = self.previewInput.getFrame()
            prg_frame = self.programInput.getFrame()

            self.total_frames += 1
            self.total_time += time.time() - self.start_time
            self.start_time = time.time()

            if self.total_time > 0:
                self.last_fps = self.total_frames / self.total_time

            if self._fade == 0:
                self.mixed_frame_ready.emit(prw_frame, prg_frame)
            else:
                if self.effectType == MIX_TYPE.FADE:
                    mix = cv2.addWeighted(prw_frame, self._fade, prg_frame, 1 - self._fade, 0)
                    self.mixed_frame_ready.emit(prw_frame, mix)
                elif self.effectType == MIX_TYPE.WIPE_LEFT_TO_RIGHT:
                    mix = self.wipeLeftToRight(prw_frame, prg_frame)
                    self.mixed_frame_ready.emit(prw_frame, mix)
                elif self.effectType == MIX_TYPE.WIPE_RIGHT_TO_LEFT:
                    mix = self.wipeRightToLeft(prw_frame, prg_frame)
                    self.mixed_frame_ready.emit(prw_frame, mix)
                elif self.effectType == MIX_TYPE.WIPE_TOP_TO_BOTTOM:
                    mix = self.wipeTopToBottom(prw_frame, prg_frame)
                    self.mixed_frame_ready.emit(prw_frame, mix)
                elif self.effectType == MIX_TYPE.WIPE_BOTTOM_TO_TOP:
                    mix = self.wipeBottomToTop(prw_frame, prg_frame)
                    self.mixed_frame_ready.emit(prw_frame, mix)
                elif self.effectType == MIX_TYPE.WIPE_STINGER:
                    if not self.isStingerLoaded:
                        self.mixed_frame_ready.emit(prw_frame, prg_frame)
                    else:
                        mix = self.stinger(prw_frame, prg_frame)
                        self.mixed_frame_ready.emit(prw_frame, mix)
                elif self.effectType == MIX_TYPE.FADE_STILL:
                    if not self.isStillLoaded:
                        self.mixed_frame_ready.emit(prw_frame, prg_frame)
                    else:
                        mix = cv2.addWeighted(self.still.getFrame(), self._fade, prg_frame, 1 - self._fade, 0)
                        self.mixed_frame_ready.emit(prw_frame, mix)
            self.fps_updated_SIGNAL.emit(self.last_fps)
            QThread.msleep(15)

    def getTally(self, tally_data):
        """
        Aggiorna lo stato del MixBus in base ai dati ricevuti dal TallyManager.
        """
        # Aggiorna i parametri come effetto e fade
        self.setFade(int(float(tally_data['fade']) * 100))
        self.effectType = MIX_TYPE[tally_data['effect'].replace(" ", "_").upper()]

        # Gestisci il preview e il program swap se necessario
        # va a cercare gli input in base ai dati ricevuti
        self.previewInput = self.crossBar[tally_data['preview']]
        self.programInput = self.crossBar[tally_data['program']]

    def get_fps(self):
        return self.last_fps

    def setFade(self, value: int):
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
        elif self.effectType == MIX_TYPE.FADE_STILL:
            self._fade += 0.01
            if self._fade > 1:
                self.autoMix_timer.stop()

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


class MixBus016T(QObject):
    mixed_frame_ready_SIGNAL = pyqtSignal(np.ndarray, np.ndarray)
    fps_updated_SIGNAL = pyqtSignal(float)

    def __init__(self, input1, input2, crossBar=None, parent=None):
        super().__init__(parent)
        self.previewInput = input1
        self.programInput = input2
        self.crossBar = crossBar
        self._fade = 0
        self.effectType = MIX_TYPE.FADE
        self.stinger_frames = []
        self.stinger_invMasks = []
        self.isStingerLoaded = False
        self.isStillLoaded = False
        self.still = None
        self._running = False
        self._wipeTime = 90
        self._init_wipe_positions()
        self.total_frames = 0
        self.total_time = 0
        self.start_time = time.time()
        self.last_fps = 0
        self.thread = QThread()  # Adding thread management from MixBus015T

        # Timer for autoMix functionality
        self.autoMix_timer = QTimer(self)
        self.autoMix_timer.timeout.connect(self._fader)

    def _init_wipe_positions(self):
        self._wipe_positions = {
            MIX_TYPE.WIPE_LEFT_TO_RIGHT: np.linspace(0, 1920, self._wipeTime),
            MIX_TYPE.WIPE_RIGHT_TO_LEFT: np.linspace(1920, 0, self._wipeTime),
            MIX_TYPE.WIPE_TOP_TO_BOTTOM: np.linspace(0, 1080, self._wipeTime),
            MIX_TYPE.WIPE_BOTTOM_TO_TOP: np.linspace(1080, 0, self._wipeTime),
        }

    def setStinger(self, stingerObject):
        self.stinger_frames = stingerObject.stingerPreMultipliedImages
        self.stinger_invMasks = stingerObject.stingerInvAlphaImages
        self.isStingerLoaded = True
        self._wipe_positions[MIX_TYPE.WIPE_STINGER] = np.linspace(0, len(self.stinger_frames) - 1, self._wipeTime)

    def setStill(self, stillObject):
        self.still = stillObject
        self.isStillLoaded = True

    def processMix(self):
        while self._running:
            mixed_preview, mixed_program = self.getMixed()
            self.mixed_frame_ready_SIGNAL.emit(mixed_preview, mixed_program)
            QThread.msleep(15)  # Simulate a frame rate of around 60 FPS

    def startProcessing(self):
        self._running = True
        self.moveToThread(self.thread)
        self.thread.started.connect(self.processMix)
        self.thread.start()

    def stop(self):
        self._running = False
        if self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()

    def getMixed(self):
        prw_frame = self.previewInput.getFrame()
        prg_frame = self.programInput.getFrame()

        self.total_frames += 1
        current_time = time.time()
        self.total_time += current_time - self.start_time
        self.start_time = current_time

        if self.total_time > 0:
            self.last_fps = self.total_frames / self.total_time
            self.fps_updated_SIGNAL.emit(self.last_fps)

        if self._fade == 0:
            return prw_frame, prg_frame

        mix_methods = {
            MIX_TYPE.FADE: lambda: cv2.addWeighted(prw_frame, self._fade, prg_frame, 1 - self._fade, 0),
            MIX_TYPE.WIPE_LEFT_TO_RIGHT: lambda: self.wipe(prw_frame, prg_frame, MIX_TYPE.WIPE_LEFT_TO_RIGHT),
            MIX_TYPE.WIPE_RIGHT_TO_LEFT: lambda: self.wipe(prw_frame, prg_frame, MIX_TYPE.WIPE_RIGHT_TO_LEFT),
            MIX_TYPE.WIPE_TOP_TO_BOTTOM: lambda: self.wipe(prw_frame, prg_frame, MIX_TYPE.WIPE_TOP_TO_BOTTOM),
            MIX_TYPE.WIPE_BOTTOM_TO_TOP: lambda: self.wipe(prw_frame, prg_frame, MIX_TYPE.WIPE_BOTTOM_TO_TOP),
            MIX_TYPE.WIPE_STINGER: lambda: self.stinger(prw_frame, prg_frame) if self.isStingerLoaded else (prw_frame, prg_frame),
            MIX_TYPE.FADE_STILL: lambda: cv2.addWeighted(self.still.getFrame(), self._fade, prg_frame, 1 - self._fade, 0) if self.isStillLoaded else (prw_frame, prg_frame),
        }

        return prw_frame, mix_methods.get(self.effectType, lambda: prw_frame)()

    def wipe(self, preview_frame, program_frame, wipe_type):
        wipe_position = int(self._wipe_positions[wipe_type][int(self._fade * (len(self._wipe_positions[wipe_type]) - 1))])
        wipe_frame = program_frame.copy()

        if wipe_type in [MIX_TYPE.WIPE_LEFT_TO_RIGHT, MIX_TYPE.WIPE_RIGHT_TO_LEFT]:
            wipe_frame[:, :wipe_position] = preview_frame[:, :wipe_position]
        else:  # Top to Bottom or Bottom to Top
            wipe_frame[:wipe_position, :] = preview_frame[:wipe_position, :]

        return wipe_frame

    def stinger(self, preview_frame, program_frame):
        _wipePosition = int(self._wipe_positions[MIX_TYPE.WIPE_STINGER][int(self._fade * (len(self._wipe_positions[MIX_TYPE.WIPE_STINGER]) - 1))])
        stinger_frame = self.stinger_frames[_wipePosition]
        inv_mask = self.stinger_invMasks[_wipePosition]

        if self._fade < 0.5:
            masked_frame = cv2.multiply(program_frame, inv_mask, dtype=cv2.CV_8U)
        else:
            masked_frame = cv2.multiply(preview_frame, inv_mask, dtype=cv2.CV_8U)

        return np.ascontiguousarray(cv2.add(stinger_frame, masked_frame))

    def setFade(self, value: int):
        self._fade = value / 100 if value > 0 else 0

    def cut(self):
        self._fade = 0
        self._wipe = 0  # Reset wipe to initial state
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
            if self._wipe > len(self._wipe_positions[self.effectType]) - 1:
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

    def getTally(self, tally_data):
        """
        Aggiorna lo stato del MixBus in base ai dati ricevuti dal TallyManager.
        """
        self.setFade(int(float(tally_data['fade']) * 100))
        self.effectType = MIX_TYPE[tally_data['effect'].replace(" ", "_").upper()]

        self.previewInput = self.crossBar[tally_data['preview']]
        self.programInput = self.crossBar[tally_data['program']]

    def get_fps(self):
        return self.last_fps


class OpenGLViewer(QOpenGLWidget):
    def __init__(self, resolution: QSize = QSize(640, 480), parent=None):
        super().__init__(parent)
        self.image = None  # Inizializza come None
        self.resolution = resolution

    def setImage(self, image):
        self.image = image
        self.update()

    def paintGL(self):
        if self.image is not None:  # Controlla che l'immagine non sia None
            if isinstance(self.image, np.ndarray):  # Verifica che sia un array NumPy
                height, width, channel = self.image.shape
                bytesPerLine = 3 * width
                qImg = QImage(self.image.data, width, height, bytesPerLine, QImage.Format.Format_RGB888)
                self.image = qImg  # Aggiorna self.image a QImage

            painter = QPainter(self)
            painter.drawImage(self.rect(), self.image)
            painter.end()

    def update_view(self, frame):
        self.setImage(frame)


class ViewersWidgets(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        self.initConnections()
        self.initGeometry()

    def initUI(self):
        self.preview = OpenGLViewer()
        self.program = OpenGLViewer()
        self.fpsLabel = QLabel("FPS: 0")

        mainLayout = QVBoxLayout()
        viewerLayout = QHBoxLayout()
        viewerLayout.addWidget(self.preview)
        viewerLayout.addWidget(self.program)
        mainLayout.addLayout(viewerLayout)
        mainLayout.addWidget(self.fpsLabel)
        self.setLayout(mainLayout)

    def initConnections(self):
        pass

    def initGeometry(self):
        self.preview.setFixedSize(640, 360)
        self.program.setFixedSize(640, 360)

    def feedSignal(self, previewFrame, programFrame):
        self.preview.update_view(previewFrame)
        self.program.update_view(programFrame)

    def updateFPSLabel(self, fps):
        self.fpsLabel.setText(f"FPS: {fps:.2f}")


class TallyManager(QObject):
    # Definisce i segnali che verranno emessi per comunicare con altri componenti
    mixBus_SIGNAL = pyqtSignal(dict)
    keyboard_SIGNAL = pyqtSignal(dict)
    monitor_SIGNAL = pyqtSignal(dict)
    camera_SIGNAL = pyqtSignal(dict)
    recorder_SIGNAL = pyqtSignal(dict)
    streaming_SIGNAL = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.isMixerAutoLocked = True  # Imposta un blocco automatico per prevenire errori

    def parseTallySignal(self, tally_data):
        """
        Interpreta i dati del segnale di tally ricevuto e decide come instradarli.
        """
        sender = tally_data.get('sender')
        if "mixBus" in sender:
            self.processMixBus(tally_data)
        elif "keyboard" in sender:
            self.processKeyboard(tally_data)
        elif "monitor" in sender:
            self.processMonitor(tally_data)
        elif "camera" in sender:
            self.processCamera(tally_data)
        elif "streaming" in sender:
            self.processStreaming(tally_data)
        elif "recorder" in sender:
            self.processRecorder(tally_data)

    def processMixBus(self, tally_data):
        pass

    def processKeyboard(self, tally_data):
        """
        La tastiera del mixer al momento manda 3 comandi di tally:
            - cut:  quando viene fatto il cut tramite pulsante, quando viene
                   premuto il tasto di un input sia esse di preview o di program
            - auto: quando viene chiamato l'autoMix
            - faderChange: quando viene mossa la slider del fader
            - effectChange: quando viene cambiato l'effetto
        :param tally_data: Es1: {'cmd': 'faderchange', 'preview': '4', 'program': '1',
                                              'effect': 'Wipe Left to Right', 'fade': 0.5}
                           Es2: {'cmd': 'cut', 'preview': '1', 'program': '4',
                                              'effect': 'Wipe Left to Right', 'fade': 0}
        :return:
        """
        cmd = tally_data.get('cmd')
        tally_data['sender'] = 'tallyManager'
        if cmd in ['cut', 'auto']:
            self.mixBus_SIGNAL.emit(tally_data)
            self.camera_SIGNAL.emit(tally_data)
            self.monitor_SIGNAL.emit(tally_data)
        elif cmd == 'faderChange':
            self.mixBus_SIGNAL.emit(tally_data)
        elif cmd == 'effectChange':
            self.mixBus_SIGNAL.emit(tally_data)

    def processMonitor(self, tally_data):
        pass

    def processCamera(self, tally_data):
        pass

    def processStreaming(self, tally_data):
        pass

    def processRecorder(self, tally_data):
        pass


class MixerKeyboard(QWidget):
    tally_SIGNAL = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.currentPreview = 1  # Preview starts with input 1 selected
        self.currentProgram = 2  # Program starts con input 2 selected

        self.inputList = ["1", "2", "3", "4"]
        self.lblInputList = ["Input 1", "Input 2", "Input 3", "Input 4"]
        self.previewBtnList = []
        self.programBtnList = []
        self.btnCut = QPushButton("CUT")
        self.btnAutoMix = QPushButton("AutoMix")
        self.sliderFade = QSlider(Qt.Orientation.Horizontal)

        self.cmbEffect = QComboBox()
        self.cmbEffect.addItems(["Fade", "Wipe Left to Right", "Wipe Right to Left"])
        self.lineEditDuration = QLineEdit("1000")
        self.autoMix_TIMER = QTimer(self)
        self.autoMix_TIMER.timeout.connect(self.faderAnimation)
        # init variables for autoMix
        self.steps = 100
        self.step_interval = 100

        # init interface
        self.initUI()
        self.initStyle()
        self.initGeometry()
        self.initConnections()

        # Set initial state
        self.initInitialState()

    def initUI(self):
        mainLayout = QVBoxLayout()
        inputNameLayout = self.createLineEditRow("input", [self.lblInputList])
        previewLayout = self.createButtonRow("prw", self.previewBtnList)
        mainLayout.addLayout(inputNameLayout)
        mainLayout.addLayout(previewLayout)

        programLayout = self.createButtonRow("prg", self.programBtnList)
        mainLayout.addLayout(programLayout)

        controlLayout = QHBoxLayout()
        controlLayout.addWidget(self.btnCut)
        controlLayout.addWidget(self.btnAutoMix)
        controlLayout.addWidget(self.sliderFade)
        controlLayout.addWidget(self.cmbEffect)
        controlLayout.addWidget(self.lineEditDuration)
        mainLayout.addLayout(controlLayout)
        self.setLayout(mainLayout)

    def createButtonRow(self, prefixName, buttonList):
        btnLayout = QHBoxLayout()
        for i in range(len(self.inputList)):
            btn = QPushButton()
            btn.setObjectName(f"{prefixName}_btn_{i + 1}")
            btn.setText("")
            btn.setCheckable(True)
            btn.setChecked(False)
            btn.clicked.connect(self.onBtnClicked)
            buttonList.append(btn)
            btnLayout.addWidget(btn)
        return btnLayout

    def createLineEditRow(self, prefixName, lineEditList):
        leLayout = QHBoxLayout()
        for i in range(len(self.inputList)):
            le = LblWidget(prefixName, i + 1, (100, 30))
            le.setObjectName(f"Input_lbl_{i + 1}")
            le.setText(self.inputList[i])
            lineEditList.append(le)
            leLayout.addWidget(le)
        return leLayout

    def initGeometry(self):
        self.sliderFade.setRange(0, 100)

    def initStyle(self):
        pass

    def initConnections(self):
        self.btnCut.clicked.connect(self.onCut)
        self.btnAutoMix.clicked.connect(self.onAutoMix)
        self.sliderFade.valueChanged.connect(self.onFade)
        self.cmbEffect.currentIndexChanged.connect(self.onEffectChange)

    def initInitialState(self):
        self.updateButtonStates()

    def onBtnClicked(self):
        btn = self.sender()
        btnName = btn.objectName()
        number = int(btnName.split("_")[-1])
        if "prw" in btnName:
            self.currentPreview = number
        elif "prg" in btnName:
            self.currentProgram = number

        self.updateButtonStates()
        self.emitTallySignal(cmd='cut')  # Emit a 'cut' command on button press

    def updateButtonStates(self):
        # Deselect all buttons first
        for btn in self.previewBtnList + self.programBtnList:
            btn.setChecked(False)

        # Select the correct preview and program buttons
        self.previewBtnList[self.currentPreview - 1].setChecked(True)
        self.programBtnList[self.currentProgram - 1].setChecked(True)

    def emitTallySignal(self, cmd):
        tally_status = {
            'sender': 'keyboard',
            'cmd': cmd,
            'preview': str(self.currentPreview),
            'program': str(self.currentProgram),
            'effect': self.cmbEffect.currentText(),
            'fade': self.sliderFade.value() / 100.0
        }
        self.tally_SIGNAL.emit(tally_status)

    def onCut(self):
        # Swap the preview and program inputs
        self.currentPreview, self.currentProgram = self.currentProgram, self.currentPreview
        # Update button states
        self.updateButtonStates()
        self.emitTallySignal(cmd='cut')  # Emit a 'cut' command
        self.sliderFade.valueChanged.disconnect(self.onFade)
        self.sliderFade.setValue(0)
        self.sliderFade.valueChanged.connect(self.onFade)

    def onAutoMix(self):
        self.emitTallySignal(cmd='auto')  # Emit an 'auto' command
        try:
            duration = int(self.lineEditDuration.text())
        except ValueError:
            duration = 100  # Default to 100ms if invalid input
            self.lineEditDuration.setText("100")

        self.steps = 100  # Number of steps to move the slider
        self.step_interval = duration // self.steps
        self.steps = 100  # Number of steps to move the slider
        self.step_interval = duration // self.steps  # Interval per step in ms
        self.sliderFade.valueChanged.disconnect(self.onFade)
        self.autoMix_TIMER.start(self.step_interval)

    def faderAnimation(self):
        if self.steps > 0:
            self.sliderFade.setValue(self.sliderFade.value() + 1)
            self.steps -= 1
        else:
            self.autoMix_TIMER.stop()
            # Swap the preview and program inputs
            self.currentPreview, self.currentProgram = self.currentProgram, self.currentPreview

            # Update button states
            self.updateButtonStates()
            self.sliderFade.setValue(0)
            self.sliderFade.valueChanged.connect(self.onFade)

    def onFade(self, value):
        print(f"Fade level: {value}")
        self.emitTallySignal(cmd='faderChange')  # Emit a 'faderchange' command

    def onEffectChange(self, index):
        print(f"Effect changed to: {self.cmbEffect.currentText()}")
        self.emitTallySignal(cmd='effectChange')

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.onAutoMix()
        elif event.key() == Qt.Key.Key_C:
            self.onCut()

    def getTally(self, tally_status):
        """Aggiorna lo stato del tastierino basato sul segnale di tally ricevuto."""
        self.currentPreview = int(tally_status['preview'])
        self.currentProgram = int(tally_status['program'])
        self.cmbEffect.setCurrentText(tally_status['effect'])
        self.sliderFade.setValue(int(float(tally_status['fade']) * 100))

        # Aggiorna lo stato dei pulsanti senza emettere segnali di tally
        self.updateButtonStates()


class MainWindowX3(QMainWindow):
    def __init__(self, something=None, parent=None):
        super().__init__(parent)
        self.synch = SynchObject()
        self.viewers = ViewersWidgets()
        self.input1 = ColorGenerator(self.synch)
        self.input2 = RandomNoiseGenerator(self.synch)
        self.mixBus = MixBus016T(self.input1, self.input2)
        self.mixerKeyboard = MixerKeyboard()
        self.tallyManager = TallyManager()
        self.mix_thread = QThread()

        self.dataManager = DataManager()

        self.initUI()
        self.initConnections()
        self.initGeometry()

    def initUI(self):
        # Inizializzazione dell'interfaccia grafica
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.viewers)
        main_layout.addWidget(self.mixerKeyboard)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def initConnections(self):
        # Connessione dei segnali tra i vari componenti
        self.mixBus.mixed_frame_ready_SIGNAL.connect(self.viewers.feedSignal)
        self.mixBus.fps_updated_SIGNAL.connect(self.viewers.updateFPSLabel)
        self.mixerKeyboard.tally_SIGNAL.connect(self.tallyManager.parseTallySignal)
        self.tallyManager.mixBus_SIGNAL.connect(self.mixBus.getTally)

        self.mixBus.moveToThread(self.mix_thread)
        self.mix_thread.started.connect(self.mixBus.startProcessing)
        self.mix_thread.start()
        self.dataManager.errorSignal.connect(self.handleError)
        self.dataManager.statusSignal.connect(print)
        self.dataManager.readySignal.connect(self.initData)
        self.dataManager.loadData()

    def initGeometry(self):
        # Inizializzazione delle variabili e degli oggetti
        self.setWindowTitle("Minimal MixBus Example")
        self.setGeometry(100, 100, 800, 600)

    def handleError(self, error):
        print(f"Error: {error}")

    def initData(self):
        self.mixBus.setStinger(self.dataManager.stingerObject)
        self.mixBus.setStill(self.dataManager.stillObject)

    def processTally(self, tally_data):
        # Esegui logiche aggiuntive o inoltra i segnali ai componenti appropriati
        print(f"Processing Tally: {tally_data}")
        self.mixerKeyboard.getTally(tally_data)

    def closeEvent(self, event):
        # Cleanup dei thread quando la finestra si chiude
        self.mixBus.stop()
        self.mix_thread.quit()
        self.mix_thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindowX3()
    window.show()
    sys.exit(app.exec())
