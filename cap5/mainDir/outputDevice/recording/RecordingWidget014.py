from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from cap5.mainDir.outputDevice.commonWidgets.codecPermutationDictionary import CODEC_PERMUTATION
from cap5.mainDir.outputDevice.commonWidgets.codecWidget014 import CodecWidget
from cap5.mainDir.outputDevice.commonWidgets.deMuxerWidget import DeMuxerWidget
from cap5.mainDir.outputDevice.recording.recordingInfoWidget import RecordingInfoWidget
from cap5.mainDir.outputDevice.recording.recordingManager import RecordingManager


class RecordingWidget014(QWidget):
    deMuxerWidget: DeMuxerWidget
    codecWidget: CodecWidget
    recordingInfoWidget: RecordingInfoWidget
    recordingManager: RecordingManager

    tally_SIGNAL = pyqtSignal(dict)

    def __init__(self, inputWidget, parent=None):
        super(RecordingWidget014, self).__init__(parent)
        self.inputWidget = inputWidget
        self.recordingManager = RecordingManager(self.inputWidget)
        self.initWidgets()
        self.initUI()
        self.initConnections()
        self.initStyle()
        self.initParams()

    def closeEvent(self, event, *args, **kwargs):
        """Sovrascrivi l'evento di chiusura per nascondere la finestra."""
        event.ignore()  # Ignora l'evento di chiusura
        self.hide()

    def showWin(self):
        self.show()

    def initWidgets(self):
        self.deMuxerWidget = DeMuxerWidget(self)
        self.codecWidget = CodecWidget(CODEC_PERMUTATION, self)
        self.recordingInfoWidget = RecordingInfoWidget(self)

    def initUI(self):
        main_layout = QHBoxLayout()
        stream_option = QVBoxLayout()
        stream_option.addWidget(self.returnGrpBox("DeMuxer", self.deMuxerWidget))
        stream_option.addWidget(self.returnGrpBox("Codec", self.codecWidget))
        main_layout.addLayout(stream_option)
        main_layout.addWidget(self.returnGrpBox("REC Info", self.recordingInfoWidget))
        self.setLayout(main_layout)

    def initConnections(self):
        self.recordingInfoWidget.startStop_SIGNAL.connect(self.onStartStopSignal)
        self.recordingManager.tally_SIGNAL.connect(self.getTally)

    def initStyle(self):
        pass

    def initParams(self):
        pass

    def initGeometry(self):
        pass

    def getTally(self, tally_data):
        sender = tally_data.get('sender')
        self.recordingInfoWidget.appendStatus(tally_data)

    def emitTallySignal(self, cmd):
        tally_status = {
            'sender': 'streaming',
            'cmd': cmd,
            'info': self.serialize(),
        }
        self.tally_SIGNAL.emit(tally_status)

    def onStartStopSignal(self, message):
        if message == "startRecording":
            self.emitTallySignal("startRecording")
            data = self.serialize()
            request = {
                "deMuxer": data["deMuxer"],
                "codec": data["codec"],
                "recInfo": data["recInfo"]
            }
            self.recordingManager.startRecording(request)
        elif message == "stopRecording":
            self.emitTallySignal("stopRecording")
            self.recordingManager.stopRecording()

    @staticmethod
    def returnGrpBox(name, widget):
        groupBox = QGroupBox(name)
        layout = QVBoxLayout()
        layout.addWidget(widget)
        groupBox.setLayout(layout)
        return groupBox



    def serialize(self):
        return {
            "deMuxer": self.deMuxerWidget.serialize(),
            "codec": self.codecWidget.serialize(),
            "recInfo": self.recordingInfoWidget.serialize()
        }

    def deserialize(self, data):
        self.deMuxerWidget.deserialize(data["deMuxer"])
        self.codecWidget.deserialize(data["codec"])
        self.recordingInfoWidget.deserialize(data["streamInfo"])


if __name__ == "__main__":
    app = QApplication([])
    window = RecordingWidget014(None)
    window.tally_SIGNAL.connect(print)
    window.show()
    app.exec()
