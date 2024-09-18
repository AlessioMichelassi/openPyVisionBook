import logging

from PyQt6.QtCore import *
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import *

logging.basicConfig(
    level=logging.DEBUG,  # Set your application level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)


class InputSignalThread(QThread):
    def __init__(self, input_id, input_object, parent=None):
        super().__init__(parent)
        self.input_id = input_id
        # input_object will be an instance of a class that inherits from baseClass like
        # RandomNoiseGenerator or ColorGenerator etc
        self.input_object = input_object
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            self.input_object.captureFrame()  # Cattura un nuovo frame
            # We start let the thread sleep for 16 ms
            # to get approximately 60 fps (1000 ms / 60 fps = 16.67 ms)
            self.msleep(16)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()

    def getFrame(self):
        return self.input_object.getFrame()


class InputDevice(QObject):
    """
    Un input è un qualsiasi input del mixer.
    Questa classe contiene il tipo di input, il nome, e gestisce la creazione di diversi tipi di input.
    """
    _frame = None
    _input_type = None
    _input_object = None
    _thread = None
    tally_SIGNAL = pyqtSignal(dict, name="tallySignal")

    def __init__(self, inputPosition, name, parent=None):
        super().__init__(parent)
        self.input_position = inputPosition
        self._name = name
        self._nickname = name

    def setName(self, name):
        """
        Name of the Object is set typically to Input_1, Input_2 etc
        :param name:
        :return:
        """
        self._name = name

    def getName(self):
        """
        Name of the Object is set typically to Input_1, Input_2 etc
        :return:
        """
        return self._name

    def getType(self):
        return self._input_type

    def setNickname(self, nickname):
        """
        In the Keyboard you can set a nickname for the input like Cam 1, Cam 2 etc
        :param nickname:
        :return:
        """
        self._nickname = nickname

    def getNickname(self):
        """
        In the Keyboard you can set a nickname for the input like Cam 1, Cam 2 etc
        :return:
        """
        return self._nickname

    def setInputObject(self, inputObject):
        """
        This sets the input object for example NoiseGenerator, ColorGenerator etc
        :param inputObject:
        :return:
        """
        self._input_object = inputObject
        self._input_type = inputObject.__class__.__name__
        if self._thread:
            self._thread.stop()
            self.emitTallySignal("warning", "You change an input object that was running, "
                                            "the thread is stopped")
            logging.warning(f"You change an input object that was running, the thread is stopped")
        self.setThread(inputObject)

    def getInputObject(self):
        """
        This return the input object for example NoiseGenerator, ColorGenerator etc
        :return:
        """
        return self._input_object

    def setThread(self, _inputObject):
        """
        This sets the thread that captures the frames
        :param _inputObject: the input object like NoiseGenerator, ColorGenerator etc
        :return:
        """
        self._thread = InputSignalThread(self._name, _inputObject)
        logging.info(
            f"INPUTDEVICE - {self._input_type} at pos: {self.input_position} Thread created for input {self._name}")

    def getThread(self):
        return self._thread

    def start(self):
        """
        This starts the thread that captures the frames
        :return:
        """
        if self._thread and not self._thread.isRunning():  # Verifica se il thread esiste e non è in esecuzione
            self._thread.start()
            self.emitTallySignal("info", "Thread started")

    def stop(self):
        """
        This stops the thread that captures the frames
        :return:
        """
        if self._thread and self._thread.isRunning():  # Verifica se il thread esiste ed è in esecuzione
            self._thread.stop()
            self.emitTallySignal("info", "Thread stopped")

    def captureFrame(self):
        """
        This captures a frame from the input object
        :return:
        """
        self._input_object.captureFrame()

    def getFrame(self):
        """
        This returns the current frame from the input object
        :return:
        """
        return self._input_object.getFrame()

    def emitTallySignal(self, cmd, message):
        tally_status = {
            'sender': f"Input_{self.input_position}",
            'cmd': cmd,
            'message': message
        }
        self.tally_SIGNAL.emit(tally_status)

    def parseTallySignal(self, data):
        pass

    def serialize(self):
        """
        This serializes the input object in a dictionary
        Practically get the variables and put them in a dictionary
        :return:
        """
        return {
            'name': self._name,
            'nickname': self._nickname,
            'type': self._input_type,
            'inputObject': self._input_object.serialize()  # Assicuriamoci che l'inputObject sia serializzabile
        }

    def deserialize(self, data):
        """
        Deserialize the input object from a dictionary
        Practically fill the variables with the data from the dictionary
        :param data:
        :return:
        """
        self._name = data["name"]
        self._input_type = data["input_type"]
