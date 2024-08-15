import sys
import numpy as np
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QColor, QBrush


class PixelGridWidget(QWidget):
    def __init__(self, _pixel_matrix, parent=None):
        super().__init__(parent)
        self.pixel_matrix = _pixel_matrix
        self.cell_size = 20  # Size of each cell in the grid

        # Set the size of the widget based on the size of the pixel matrix
        rows, cols = self.pixel_matrix.shape
        self.setFixedSize(cols * self.cell_size, rows * self.cell_size)

    def paintEvent(self, event):
        painter = QPainter(self)
        rows, cols = self.pixel_matrix.shape

        for row in range(rows):
            for col in range(cols):
                intensity = self.pixel_matrix[row, col]
                color_value = int(255 * (1 - intensity))  # Convert intensity to color (0-255)
                color = QColor(color_value, color_value, color_value)  # Create grayscale color
                painter.fillRect(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size,
                                 QBrush(color))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Create a random pixel intensity matrix (values between 0 and 1)
    pixel_matrix = np.random.rand(10, 10)

    # Create and show the widget
    widget = PixelGridWidget(pixel_matrix)
    widget.show()

    sys.exit(app.exec())
