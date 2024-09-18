from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

from cap5.mainDir.outputDevice.commonWidgets.codecPermutationDictionary import CODEC_PERMUTATION
from cap5.mainDir.outputDevice.commonWidgets.codecWidget014 import CodecWidget
from cap5.mainDir.outputDevice.commonWidgets.deMuxerWidget import DeMuxerWidget
from cap5.mainDir.outputDevice.streaming.streamInfoWidget014 import StreamInfoWidget
from cap5.mainDir.outputDevice.streaming.streamingManager016 import StreamerManager016


class StreamingWidget016(QWidget):
    deMuxerWidget: DeMuxerWidget
    codecWidget: CodecWidget
    streamInfoWidget: StreamInfoWidget
    streamerManager: StreamerManager016

    tally_SIGNAL = pyqtSignal(dict)

    def __init__(self, inputWidget, parent=None):
        super(StreamingWidget016, self).__init__(parent)
        self.inputWidget = inputWidget
        self.streamerManager = StreamerManager016(self.inputWidget)
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
        self.streamInfoWidget = StreamInfoWidget(self)

    def initUI(self):
        main_layout = QHBoxLayout()
        stream_option = QVBoxLayout()
        stream_option.addWidget(self.returnGrpBox("DeMuxer", self.deMuxerWidget))
        stream_option.addWidget(self.returnGrpBox("Codec", self.codecWidget))
        main_layout.addLayout(stream_option)
        main_layout.addWidget(self.returnGrpBox("Stream Info", self.streamInfoWidget))
        self.setLayout(main_layout)

    def initConnections(self):
        self.streamInfoWidget.startStop_SIGNAL.connect(self.onStartStopSignal)
        self.streamerManager.tally_SIGNAL.connect(self.getTallyFromManager)

    def initStyle(self):
        pass

    def initParams(self):
        pass

    def initGeometry(self):
        pass

    def getTally(self, tally_data):
        sender = tally_data.get('sender')
        print(f"WARNING FROM STREAMING WIDGET: Tally signal received from {sender}")
        print("FUNCTION GET NOT YET IMPLEMENTED!")
        print(f"data was: {tally_data}")

    def getTallyFromManager(self, tally_data):
        self.streamInfoWidget.txtStatus.append(tally_data.get('info'))

    def emitTallySignal(self, cmd):
        tally_status = {
            'sender': 'streaming',
            'cmd': cmd,
            'info': self.serialize(),
        }
        self.tally_SIGNAL.emit(tally_status)

    def onStartStopSignal(self, message):
        if message == "startStream":
            self.emitTallySignal("startStream")
            data = self.serialize()
            request = {
                "deMuxer": data["deMuxer"],
                "codec": data["codec"],
                "streamInfo": data["streamInfo"]
            }
            self.streamerManager.startStreaming(request)
        elif message == "stopStream":
            self.emitTallySignal("stopStream")
            self.streamerManager.stopStreaming()

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
            "streamInfo": self.streamInfoWidget.serialize()
        }

    def deserialize(self, data):
        self.deMuxerWidget.deserialize(data["deMuxer"])
        self.codecWidget.deserialize(data["codec"])
        self.streamInfoWidget.deserialize(data["streamInfo"])


if __name__ == "__main__":
    app = QApplication([])
    window = StreamingWidget016(None)
    window.tally_SIGNAL.connect(print)
    window.show()
    app.exec()
