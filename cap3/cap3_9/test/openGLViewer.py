from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtOpenGLWidgets import QOpenGLWidget


class OpenGLViewer(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage()

    def setImage(self, image):
        self.image = image
        self.update()

    def paintGL(self):
        if not self.image.isNull():
            painter = QPainter(self)
            painter.drawImage(self.rect(), self.image)
            painter.end()