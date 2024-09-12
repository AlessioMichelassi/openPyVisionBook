from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from cap5.mainDir.outputs.openGLViewer import OpenGLViewer


class MainOut(QWidget):
    _isStayOnTop = False

    def __init__(self, resolution=QSize(1920, 1080), parent=None):
        super().__init__(parent)
        self._viewer = OpenGLViewer(resolution)
        self._output = None
        self.initUI()
        self.initGeometry()
        self.initConnections()

    def initUI(self):
        """
        This function initializes the UI.
        :return:
        """
        mainLayout = QVBoxLayout()
        viewerLayout = QHBoxLayout()
        viewerLayout.addWidget(self._viewer)
        mainLayout.addLayout(viewerLayout)
        self.setLayout(mainLayout)

    def initGeometry(self):
        self._viewer.setFixedSize(1920, 1080)

    def initConnections(self):
        # Puoi aggiungere connessioni qui, se necessario
        pass

    def feedOutput(self, out):
        self._output = out
        self._viewer.setImage(out)

    def getOut(self):
        return self._output

    def toggleFullScreen(self):
        """
        This function toggles the full screen mode.
        :return:
        """
        if not self.isFullScreen:
            self.showFullScreen()
        else:
            self.showNormal()

    def toggleStayOnTop(self):
        """
        This function toggles the stay on top mode.
        :return:
        """
        if not self._isStayOnTop:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            self._isStayOnTop = True
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
            self._isStayOnTop = False
        self.show()

    def keyPressEvent(self, event, _QKeyEvent=None):
        if event.key() == Qt.Key.Key_F:
            self.toggleFullScreen()
        elif event.key() == Qt.Key.Key_T:
            self.toggleStayOnTop()
        super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    window = MainOut()
    window.show()
    app.exec()
