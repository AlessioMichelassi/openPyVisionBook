import cv2
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget


class OpenGLViewer(QOpenGLWidget):
    def __init__(self, resolution: QSize = QSize(640, 360), parent=None):
        super().__init__(parent)
        self.image = QImage()
        self.resolution = resolution

    def setImage(self, image):
        # fra il resize e l'update, l'immagine viene ridimensionata
        self.image = image
        self.update()

    def paintGL(self):
        if not self.image is None:
            painter = QPainter(self)
            painter.drawImage(self.rect(), self.image)
            painter.end()
