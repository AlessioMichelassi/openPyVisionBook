import json
import logging

from PyQt6.QtCore import QObject, pyqtSignal

from cap5.cap5_3.videoHub.inputDevice.generatorDevice.inputDevice_blackGenerator import InputDevice_BlackGenerator
from cap5.cap5_3.videoHub.inputDevice.generatorDevice.inputDevice_colorGenerator import InputDevice_ColorGenerator
from cap5.cap5_3.videoHub.inputDevice.generatorDevice.inputDevice_noiseGenerator import InputDevice_NoiseGenerator
from cap5.cap5_3.videoHub.inputDevice.playerDevice.inputDevice_stillImagePlayerGenerator import \
    InputDevice_StillImagePlayer
from cap5.mainDir.inputs.generator.generator_Black import BlackGenerator

logging.basicConfig(
    level=logging.DEBUG,  # Set your application level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

"""# Set the logging level for comtypes to WARNING to suppress debug output
logging.getLogger('comtypes').setLevel(logging.WARNING)
logging.getLogger('comtypes._post_coinit.unknwn').setLevel(logging.WARNING)

# Similarly, if other libraries are too verbose
logging.getLogger('some_other_library').setLevel(logging.ERROR)"""


class VideoHubData018(QObject):
    _blackSignal = None
    tally_SIGNAL = pyqtSignal(dict, name="tallySignal")

    def __init__(self, parent=None):
        super().__init__(parent)
        self.videoHubMatrix = {}
        for i in range(0,9):
            self.addInputDevice(i, self.returnDefaultBlackInput())

        """self._stingerInput1 = self.returnDefaultBlackInput()
        self._stingerInput2 = self.returnDefaultBlackInput()
        self._stillImageInput1 = self.returnDefaultBlackInput()
        self._stillImageInput2 = self.returnDefaultBlackInput()
        self._stillImageInput3 = self.returnDefaultBlackInput()
        self._stillImageInput4 = self.returnDefaultBlackInput()"""

    @staticmethod
    def returnDefaultBlackInput():
        """
        Restituisce una nuova istanza dell'input predefinito nero.
        """
        blackInput = BlackGenerator()
        return InputDevice_BlackGenerator("Black", blackInput)

    def addInputDevice(self, position, inputDevice):
        """
        This adds an input device to the video hub matrix at the given position,
        but only if it is different from the current one.
        """
        current_device = self.getInputDevice(position)
        if current_device and current_device.getType() == inputDevice.getType():
            logging.info(f"Input device at position {position} already exists with the same type.")
            return
        logging.info(f"VIDEOHUBDATA - Adding new input device at position {position}")
        self.videoHubMatrix[position] = inputDevice

    def getInputDevice(self, position):
        return self.videoHubMatrix.get(position)

    def removeInputDevice(self, position):
        """
        This removes an input device from the video hub matrix at the given position.
        """
        if self.videoHubMatrix[position].getThread() is not None:
            if self.videoHubMatrix[position].getThread().isRunning():
                self.stopInputDevice(position)
        self.videoHubMatrix[position] = self.returnDefaultBlackInput()

    def startInputDevice(self, position):
        inputDevice = self.videoHubMatrix.get(position)
        if inputDevice and inputDevice.getThread() and not inputDevice.getThread().isRunning():
            inputDevice.start()
            logging.info(f"VIDEOHUBDATA -Thread started for input at position {position}")

    def stopInputDevice(self, position):
        inputDevice = self.videoHubMatrix.get(position)
        if inputDevice and inputDevice.getThread() and inputDevice.getThread().isRunning():
            inputDevice.stop()
            logging.info(f"VIDEOHUBDATA -Thread stopped for input at position {position}")

    def emitTallySignal(self, cmd, position):
        tally_status = {
            'sender': 'videoHub',
            'cmd': cmd,
            'position': position,
        }
        self.tally_SIGNAL.emit(tally_status)
        logging.debug(f"VIDEOHUBDATA -Emesso segnale tally: {tally_status}")

    def parseTallySignal(self, data):
        """
        This function parses the tally signal and performs the action accordingly.
        """
        cmd = data['cmd']
        position = data['position']

        if cmd == "startInput":
            logging.info(f"VIDEOHUBDATA -Starting input at position {position}")
            self.startInputDevice(position)
        elif cmd == "stopInput":
            logging.info(f"VIDEOHUBDATA -Stopping input at position {position}")
            self.stopInputDevice(position)

        elif cmd == "removeInput":
            logging.info(f"VIDEOHUBDATA -Removing input at position {position}")
            self.removeInputDevice(position)
        else:
            logging.warning(f"VIDEOHUBDATA -Unknown tally command: {cmd} for position {position}")

    def serialize(self):
        data = {}
        for position, _input in self.videoHubMatrix.items():
            if _input:
                try:
                    data[position] = _input.serialize()
                except Exception as e:
                    logging.error(f"VIDEOHUBDATA -Error serializing input at position {position}: {e}")
        return data

    def deserialize(self, data):
        for position, input_data in data.items():
            try:
                if input_data:  # Controlla che input_data non sia None
                    self.parseData(position, input_data)
            except Exception as e:
                logging.error(f"VIDEOHUBDATA -Error deserializing input at position {position}: {e}")

    def parseData(self, position, input_data):
        """
        This function parses the input data and creates the corresponding input device.
        """
        input_type = input_data.get('type')  # Assumendo che ci sia una chiave 'type' nei dati
        if input_type == "BlackGenerator":
            input_device = InputDevice_BlackGenerator("Black", BlackGenerator())
            logging.debug(f"VIDEOHUBDATA -Black generator added at position {position}")
        elif input_type == "ColorGenerator":
            input_device = InputDevice_ColorGenerator("ColorGenerator")
            logging.debug(f"VIDEOHUBDATA -Color generator added at position {position}")
            input_device.deserialize(input_data)
        elif input_type == "NoiseGenerator":
            input_device = InputDevice_NoiseGenerator("NoiseGenerator")
            logging.debug(f"VIDEOHUBDATA -Noise generator added at position {position}")
            input_device.deserialize(input_data)
        elif input_type == "StillImagePlayer":
            input_device = InputDevice_StillImagePlayer("StillImagePlayer")
            logging.debug(f"VIDEOHUBDATA -Still image player added at position {position}")
            input_device.deserialize(input_data)
        else:
            logging.error(f"VIDEOHUBDATA -Unknown input type: {input_type} at position {position}")
            return

        # Aggiungi l'input device alla posizione corretta senza avviare il thread
        self.addInputDevice(position, input_device)

        # Emetti segnale di deserializzazione completata
        self.emitTallySignal("inputAdded", position)

        # Aggiungi l'input device alla posizione corretta senza avviare il thread
        self.addInputDevice(position, input_device)

        # Emetti segnale di deserializzazione completata
        self.emitTallySignal("inputAdded", position)