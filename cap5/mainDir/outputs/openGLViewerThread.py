import cv2
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget


class ImageConverterThread(QThread):
    imageReady = pyqtSignal(QImage)

    def __init__(self, numpy_array, parent=None):
        super().__init__(parent)
        self.numpy_array = numpy_array

    def run(self):
        # Conversione dell'array NumPy in QImage
        height, width, channel = self.numpy_array.shape
        bytesPerLine = 3 * width
        qImg = QImage(self.numpy_array.data, width, height, bytesPerLine, QImage.Format.Format_BGR888)
        qImg = qImg.copy()
        self.imageReady.emit(qImg)


class OpenGLViewerThread(QOpenGLWidget):
    def __init__(self, resolution: QSize = QSize(640, 360), parent=None):
        super().__init__(parent)
        self.image = QImage()
        self.resolution = resolution
        self.converter_thread = None

    def setImage(self, image):
        self.image = image
        self.update()

    def setNumpyArray(self, numpy_array):
        # Avvia un thread per la conversione
        self.converter_thread = ImageConverterThread(numpy_array)
        self.converter_thread.imageReady.connect(self.setImage)
        self.converter_thread.start()

    def paintGL(self):
        if not self.image.isNull():
            painter = QPainter(self)
            painter.drawImage(self.rect(), self.image)
            painter.end()
