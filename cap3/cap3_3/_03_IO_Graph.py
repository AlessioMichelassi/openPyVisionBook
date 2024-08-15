import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt


class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Graph Widget')
        self.setGeometry(100, 100, 400, 450)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("Inserisci l'operazione (es. *1.2, +0.4, (x-0.33)*3)")
        self.input_box.textChanged.connect(self.update_graph)
        self.layout.addWidget(self.input_box)

        self.graph_widget = GraphDrawingWidget()
        self.layout.addWidget(self.graph_widget)

    def update_graph(self, text):
        self.graph_widget.update_curve(text)


class GraphDrawingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(400, 400)

        # Define colors
        self.gridColor = QColor(200, 200, 200)
        self.axisColor = QColor(255, 0, 0)
        self.lineColor = QColor(0, 0, 0)
        self.dotLineColor = QColor(155, 155, 155)
        self.textColor = QColor(0, 0, 255)

        self.expression = 'x'
        self.curve = np.linspace(0, 1, 100)
        self.update_curve(self.expression)

    def update_curve(self, expression):
        self.expression = expression
        x = np.linspace(0, 1, 100)
        try:
            y = eval(self.expression)
            self.curve = np.clip(y, 0, 1)
        except Exception as e:
            self.curve = x  # If there's an error, revert to the identity curve
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Background
        painter.fillRect(self.rect(), Qt.GlobalColor.white)

        # Draw the grid
        painter.setPen(QPen(self.gridColor, 1, Qt.PenStyle.SolidLine))
        for x in range(0, self.width(), 20):
            painter.drawLine(x, 0, x, self.height())
        for y in range(0, self.height(), 20):
            painter.drawLine(0, y, self.width(), y)

        # Draw the axes
        painter.setPen(QPen(self.axisColor, 2, Qt.PenStyle.SolidLine))
        painter.drawLine(50, self.height() - 50, self.width() - 50, self.height() - 50)  # X axis
        painter.drawLine(50, self.height() - 50, 50, 50)  # Y axis

        # Draw labels and ticks
        painter.setPen(QPen(self.textColor, 2))
        painter.setFont(painter.font())
        painter.drawText(self.width() - 50, self.height() - 30, 'INPUT')
        painter.drawText(10, 40, 'OUTPUT')
        painter.drawText(35, self.height() - 55, '0')
        painter.drawText(self.width() - 60, self.height() - 55, '1')
        painter.drawText(35, (self.height() - 50) // 2 + 15, '0.5')
        painter.drawText((self.width() - 50) // 2, self.height() - 30, '0.5')

        # Draw the curve
        painter.setPen(QPen(self.lineColor, 2, Qt.PenStyle.SolidLine))
        for i in range(1, len(self.curve)):
            start_x = 50 + (self.width() - 100) * (i - 1) / (len(self.curve) - 1)
            end_x = 50 + (self.width() - 100) * i / (len(self.curve) - 1)
            start_y = self.height() - 50 - (self.height() - 100) * self.curve[i - 1]
            end_y = self.height() - 50 - (self.height() - 100) * self.curve[i]
            painter.drawLine(int(start_x), int(start_y), int(end_x), int(end_y))

        # Draw dashed lines
        pen = QPen(self.dotLineColor, 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawLine(50, 50, self.width() - 50, 50)  # Line from (0,1) to (1,1)
        painter.drawLine(self.width() - 50, self.height() - 50, self.width() - 50, 50)  # Line from (1,0) to (1,1)

        painter.end()


def main():
    app = QApplication(sys.argv)
    widget = GraphWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
