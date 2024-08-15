import cv2
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget


class OpenGLViewer(QOpenGLWidget):
    def __init__(self, resolution: QSize = QSize(1280, 720), parent=None):
        super().__init__(parent)
        self.image = QImage()
        self.resolution = resolution

    def setImage(self, image):
        # fra il resize e l'update, l'immagine viene ridimensionata
        self.image = image.scaled(self.resolution.width(), self.resolution.height())
        self.update()

    def paintGL(self):
        if not self.image.isNull():
            painter = QPainter(self)
            painter.drawImage(self.rect(), self.image)
            painter.end()
