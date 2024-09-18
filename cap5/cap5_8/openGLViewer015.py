import numpy as np
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

import logging

# Configura il logging
logging.basicConfig(level=logging.DEBUG)


class OpenGLViewer015(QOpenGLWidget):
    isThread = True  # Set to True to use threading

    def __init__(self, resolution: QSize = QSize(640, 360), isFullScreen=False, parent=None):
        super().__init__(parent)
        self.image = QImage()
        self._numpyFrame = np.zeros((resolution.height(), resolution.width(), 3), np.uint8)
        self.resolution = resolution
        logging.debug("OpenGLViewer015: Initialized.")

    def setFrame(self, _numpyArray):
        """
        Sends the NumPy frame for conversion to QImage on a thread from the pool.
        """

        self._numpyFrame = _numpyArray
        try:
            self.image = QImage(
                self._numpyFrame.data,
                self._numpyFrame.shape[1],
                self._numpyFrame.shape[0],
                self._numpyFrame.strides[0],
                QImage.Format.Format_BGR888
            )
            self.update()
        except Exception as e:
            logging.exception(f"OpenGLViewer015: Exception during QImage creation: {e}")

    def getFrame(self):
        return self._numpyFrame

    def setQImage(self, qImage: QImage):
        """
        Sets the converted QImage and updates the OpenGL widget.
        """
        self.image = qImage
        self.update()

    def getQImage(self):
        return self.image

    def paintGL(self):
        if not self.image.isNull():
            # logging.debug("OpenGLViewer015: Painting QImage.")
            painter = QPainter(self)
            painter.drawImage(self.rect(), self.image)
            painter.end()
        else:
            logging.debug("OpenGLViewer015: No image to paint.")
