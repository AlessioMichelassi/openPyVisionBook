import numpy as np
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject


class FrameConverter(QRunnable):
    """
    QRunnable per convertire un frame NumPy in QImage.
    Emana un segnale quando la conversione è completata.
    """

    class Signals(QObject):
        finished = pyqtSignal(QImage)

    def __init__(self, numpy_frame):
        super().__init__()
        self.numpy_frame = numpy_frame
        self.signals = self.Signals()

    def run(self):
        try:
            # Assicurati che il frame sia contiguo in memoria
            if not self.numpy_frame.flags['C_CONTIGUOUS']:
                self.numpy_frame = np.ascontiguousarray(self.numpy_frame)

            height, width, channel = self.numpy_frame.shape
            bytes_per_line = 3 * width
            qImage = QImage(self.numpy_frame.data, width, height, bytes_per_line, QImage.Format.Format_BGR888).copy()
            self.signals.finished.emit(qImage)
        except Exception as e:
            print(f"Error in FrameConverter: {e}")


class OpenGLViewerThread016(QOpenGLWidget):

    def __init__(self, resolution: QSize = QSize(640, 360), isFullScreen=False, parent=None):
        super().__init__(parent)
        self.image = QImage()
        self._numpyFrame = np.zeros((resolution.height(), resolution.width(), 3), np.uint8)
        self.resolution = resolution
        self.threadpool = QThreadPool()  # Crea un threadpool
        self.threadpool.setMaxThreadCount(4)  # Limita il numero di thread simultanei

    def setFrame(self, _numpyArray):
        """
        Invia il frame NumPy per la conversione in QImage su un thread del pool.
        """
        self._numpyFrame = _numpyArray.copy()  # Copia per evitare modifiche durante la conversione
        self.start_conversion_thread()

    def getFrame(self):
        return self._numpyFrame

    def start_conversion_thread(self):
        # Crea un nuovo QRunnable per la conversione del frame
        converter = FrameConverter(self._numpyFrame)
        converter.signals.finished.connect(self.setQImage)
        self.threadpool.start(converter)

    @pyqtSlot(QImage)
    def setQImage(self, qImage: QImage):
        """
        Imposta il QImage convertito e aggiorna il widget OpenGL.
        """
        self.image = qImage
        self.update()

    def getQImage(self):
        return self.image

    def paintGL(self):
        if not self.image.isNull():
            painter = QPainter(self)
            # Disegna l'immagine mantenendo le proporzioni
            painter.drawImage(self.rect(), self.image)
            painter.end()
