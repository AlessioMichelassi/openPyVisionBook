from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *


class DeMuxerWidget(QWidget):
    cmbDeMuxer: QComboBox
    cmbVideoInputFormat: QComboBox
    cmbAudioInputFormat: QComboBox

    def __init__(self, parent=None):
        super(DeMuxerWidget, self).__init__(parent)
        self.initWidgets()
        self.initUI()
        self.initConnections()
        self.initStyle()
        self.initParams()

    def initWidgets(self):
        self.cmbDeMuxer = QComboBox(self)
        self.cmbVideoInputFormat = QComboBox(self)
        self.cmbAudioInputFormat = QComboBox(self)

    def initUI(self):
        main_layout = QVBoxLayout()
        video_layout = self.returnHLayout(QLabel("Video Input Format:"),
                                          self.cmbVideoInputFormat)
        audio_layout = self.returnHLayout(QLabel("Audio Input Format:"),
                                          self.cmbAudioInputFormat)
        main_layout.addWidget(QLabel("DeMuxer:"))
        main_layout.addWidget(self.cmbDeMuxer)
        main_layout.addLayout(video_layout)
        main_layout.addLayout(audio_layout)
        self.setLayout(main_layout)

    @staticmethod
    def returnHLayout(*args):
        layout = QHBoxLayout()
        for arg in args:
            layout.addWidget(arg)
        return layout

    def initConnections(self):
        pass

    def initStyle(self):
        pass

    def initParams(self):
        self.cmbDeMuxer.addItems(['rawvideo', 'mp4', 'flv', 'avi', 'rtmp', 'rtsp'])
        self.cmbVideoInputFormat.addItems(['rawvideo', 'mp4', 'flv', 'avi', 'rtmp', 'rtsp'])
        self.cmbAudioInputFormat.addItems(['anullsrc', "s16", "s32", "fltp"])

    def serialize(self):
        return {
            "deMuxer": self.cmbDeMuxer.currentText(),
            "videoInputFormat": self.cmbVideoInputFormat.currentText(),
            "audioInputFormat": self.cmbAudioInputFormat.currentText()
        }

    def deserialize(self, data):
        self.cmbDeMuxer.setCurrentText(data["deMuxer"])
        self.cmbVideoInputFormat.setCurrentText(data["videoInputFormat"])
        self.cmbAudioInputFormat.setCurrentText(data["audioInputFormat"])


if __name__ == "__main__":
    app = QApplication([])
    win = DeMuxerWidget()
    win.show()
    app.exec()
