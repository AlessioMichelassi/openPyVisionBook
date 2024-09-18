from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from cap5.cap5_9.MrKeyboard.mixerKeyboard.blinkingButton import BlinkingButton
from cap5.cap5_9.MrKeyboard.styles.btnStyle import btnRedStyle


class StreamInfoWidget(QWidget):
    url_input: QLineEdit
    key_input: QLineEdit
    btnStartStream: BlinkingButton
    txtStatus: QTextEdit
    isStreaming: bool = False

    startStop_SIGNAL = pyqtSignal(str)

    def __init__(self, parent=None):
        super(StreamInfoWidget, self).__init__(parent)
        self.initWidgets()
        self.initUI()
        self.initConnections()
        self.initStyle()
        self.initParams()

    def initWidgets(self):
        self.url_input = QLineEdit("rtmp://a.rtmp.youtube.com/live2")
        self.key_input = QLineEdit("uqxj-qmuz-3dqv-9sck-as31")
        self.btnStartStream = BlinkingButton("Start Streaming")
        self.txtStatus = QTextEdit()

    def initUI(self):
        mainLayout = QVBoxLayout()
        url_label = QLabel("Stream URL (e.g., rtmp://a.rtmp.youtube.com/live2):")
        key_label = QLabel("Stream Key:")
        mainLayout.addWidget(url_label)
        mainLayout.addWidget(self.url_input)
        mainLayout.addWidget(key_label)
        mainLayout.addWidget(self.key_input)
        mainLayout.addWidget(self.btnStartStream)
        mainLayout.addWidget(self.txtStatus)
        self.setLayout(mainLayout)

    def initConnections(self):
        self.btnStartStream.clicked.connect(self.startStream)

    def initStyle(self):
        self.btnStartStream.setStyleSheet(btnRedStyle)

    def initParams(self):
        self.btnStartStream.setCheckable(True)
        self.txtStatus.setReadOnly(True)

    def initGeometry(self):
        pass

    def getStreamerMessage(self, message):
        self.txtStatus.append(message)
        if "streamStopped" in message:
            self.btnStartStream.stopBlinking()
            self.isStreaming = False

    def startStream(self):
        if self.isStreaming:
            self.startStop_SIGNAL.emit("stopStream")
            self.isStreaming = False
            self.btnStartStream.setText("Start Streaming")
            self.txtStatus.append("send request to stop Streaming.")
            self.btnStartStream.stopBlinking()
        else:
            self.startStop_SIGNAL.emit("startStream")
            self.txtStatus.append("send request to start Streaming.")
            self.btnStartStream.setText("Stop Streaming")
            self.isStreaming = True
            self.btnStartStream.startBlinking()

    def serialize(self):
        return {
            "url": self.url_input.text(),
            "key": self.key_input.text()
        }

    def deserialize(self, data):
        self.url_input.setText(data["url"])
        self.key_input.setText(data["key"])

    def clear(self):
        self.url_input.clear()
        self.key_input.clear()
        self.txtStatus.clear()
        self.isStreaming = False

    def setStreaming(self, isStreaming: bool):
        self.isStreaming = isStreaming
        self.btnStartStream.setChecked(isStreaming)


if __name__ == "__main__":
    app = QApplication([])
    w = StreamInfoWidget()
    w.show()
    app.exec()
