from PyQt6.QtCore import QObject, pyqtSignal


class TallyManager(QObject):
    # Definisce i segnali che verranno emessi per comunicare con altri componenti
    mixBus_SIGNAL = pyqtSignal(dict)
    mixEffect_SIGNAL = pyqtSignal(dict)
    keyboard_SIGNAL = pyqtSignal(dict)
    monitor_SIGNAL = pyqtSignal(dict)
    camera_SIGNAL = pyqtSignal(dict)
    recorder_SIGNAL = pyqtSignal(dict)
    streaming_SIGNAL = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

    def parseTallySignal(self, tally_data):
        """
        Interpreta i dati del segnale di tally ricevuto e decide come instradarli.
        """
        sender = tally_data.get('sender')
        if "mixBus" in sender:
            self.processMixBus(tally_data)
        elif "keyboard" in sender:
            self.processKeyboard(tally_data)
        elif "videoHub" in sender:
            self.processVideoHub(tally_data)
        elif "monitor" in sender:
            self.processMonitor(tally_data)
        elif "camera" in sender:
            self.processCamera(tally_data)
        elif "streaming" in sender:
            self.processStreaming(tally_data)
        elif "recorder" in sender:
            self.processRecorder(tally_data)
        else:
            self.processUnknownSender(tally_data)

    def processMixBus(self, tally_data):
        # Aggiungi logica se necessario
        pass

    def processKeyboard(self, tally_data):
        cmd = tally_data.get('cmd')
        tally_data['sender'] = 'tallyManager'
        valid_commands = ['cut', 'auto', 'faderChange', 'effectChange', 'previewChange', 'programChange']
        if cmd in valid_commands:
            self.mixBus_SIGNAL.emit(tally_data)
            if cmd in ['previewChange', 'programChange']:
                self.mixEffect_SIGNAL.emit(tally_data)
        else:
            print(f"WARNING FROM TALLY MANAGER: Invalid command from Keyboard: {cmd}\n{tally_data}")

    def processVideoHub(self, tally_data):
        print(f"TALLY MANAGER: Video Hub signal received {tally_data}")
        cmd = tally_data.get('cmd')
        tally_data['sender'] = 'tallyManager'
        valid_commands = ['inputChanged', 'inputRemoved','stillImageReady', 'stingerReady']
        if cmd in valid_commands:
            self.mixBus_SIGNAL.emit(tally_data)
        else:
            print(f"WARNING FROM TALLY MANAGER: Invalid command from VideoHub: {cmd}\n{tally_data}")

    def processMonitor(self, tally_data):
        pass

    def processCamera(self, tally_data):
        pass

    def processStreaming(self, tally_data):
        pass

    def processRecorder(self, tally_data):
        pass

    def processUnknownSender(self, tally_data):
        print(f"WARNING FROM TALLY MANAGER: Unknown sender: {tally_data['sender']}\n{tally_data}")
