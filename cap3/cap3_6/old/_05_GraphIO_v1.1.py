import sys
import numpy as np
import cv2
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout, QPushButton, QFileDialog
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap, QImage, QPalette
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


class ImageProcessor:
    @staticmethod
    def apply_expression(img, expression):
        x = img / 255.0  # Normalizzare l'immagine
        y = eval(expression, {"x": x, "np": np})  # Eval con contesto sicuro
        y = np.clip(y, 0, 1)
        return np.uint8(y * 255)

    @staticmethod
    def compute_histogram(img):
        hist, bins = np.histogram(img.flatten(), 256, [0, 256])
        fig, ax = plt.subplots(figsize=(5, 4))

        # Impostare uno sfondo scuro e una griglia
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        ax.grid(color='gray', linestyle='--', linewidth=0.5)

        ax.plot(hist, color='white')
        ax.set_xlim([0, 256])
        ax.set_xlabel("Valore del pixel", color='white')
        ax.set_ylabel("Frequenza", color='white')
        ax.set_title("Istogramma", color='white')

        ax.tick_params(colors='white')

        canvas = FigureCanvas(fig)
        canvas.draw()
        width, height = fig.get_size_inches() * fig.get_dpi()
        image = np.frombuffer(canvas.tostring_rgb(), dtype='uint8').reshape(int(height), int(width), 3)
        plt.close(fig)

        return QImage(image.data, image.shape[1], image.shape[0], QImage.Format.Format_RGB888)


class GraphWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('IO+ - The Graph Widget v0.1')

        # Init widgets
        self.open_button = QPushButton('Open Image', self)
        self.input_box = QLineEdit(self)
        self.input_box.setPlaceholderText("Formula HERE: (es. x*1.2, x+0.4, (x-0.33)*3) where x is the image")
        self.graph_widget = GraphDrawingWidget()
        self.image_label = QLabel(self)
        self.hist_label = QLabel(self)
        self.orig_image_label = QLabel(self)

        self.image_path = None
        self.orig_img = None

        self.init_ui()
        self.init_connections()
        self.init_geometry()
        self.init_style()

    def init_ui(self):
        main_layout = QVBoxLayout()
        upper_layout = QHBoxLayout()
        upper_layout.addWidget(self.orig_image_label)
        upper_layout.addWidget(self.image_label)
        lower_layout = QHBoxLayout()
        lower_layout.addWidget(self.hist_label)
        lower_layout.addWidget(self.graph_widget)
        main_layout.addLayout(upper_layout)
        main_layout.addLayout(lower_layout)
        main_layout.addWidget(self.input_box)
        main_layout.addWidget(self.open_button)
        self.setLayout(main_layout)

    def init_connections(self):
        self.open_button.clicked.connect(self.on_open_image)
        self.input_box.textChanged.connect(self.on_update_graph)

    def init_geometry(self):
        self.setGeometry(100, 100, 1200, 800)

    def init_style(self):
        # Stile delle QLabel e QPushButton
        style = """
        QLabel {
            background-color: black;
            border: 1px solid #FFFFFF;
            min-height: 300px;
        }
        QPushButton {
            font-size: 16px;
        }
        QLineEdit {
            background-color: black;
            color: rgb(200, 200, 200);
            placeholder-text-color: rgb(250, 100, 100);
            selection-color: white;
            selection-background-color: red;
            border: 1px solid #FFFFFF;
            padding: 10px;
            font-size: 16px;
        }
        """
        self.setStyleSheet(style)

    def on_open_image(self):
        options = QFileDialog.Option.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, 'Apri immagine', '', 'Image Files (*.png *.jpg *.bmp)',
                                                   options=options)
        if file_name:
            self.image_path = file_name
            self.orig_img = cv2.imread(self.image_path, cv2.IMREAD_GRAYSCALE)
            if self.orig_img is None:
                raise ValueError("Immagine non valida")
            self.orig_img = cv2.resize(self.orig_img, (256, 256), interpolation=cv2.INTER_NEAREST)
            self.display_image(self.orig_img, self.orig_image_label)
            self.update_image_and_histogram(self.input_box.text())

    def on_update_graph(self, text):
        self.graph_widget.update_curve(text)
        if self.orig_img is not None:
            self.update_image_and_histogram(text)

    def update_image_and_histogram(self, text):
        try:
            if self.orig_img is None:
                raise ValueError("Immagine non valida")

            img = ImageProcessor.apply_expression(self.orig_img, text)
            hist_img = ImageProcessor.compute_histogram(img)

            self.hist_label.setPixmap(QPixmap.fromImage(hist_img))
            self.display_image(img, self.image_label)

        except Exception as e:
            print(f"Errore nell'aggiornamento dell'immagine e dell'istogramma: {e}")

    def display_image(self, img, label):
        q_img = QImage(img.data, img.shape[1], img.shape[0], img.strides[0], QImage.Format.Format_Grayscale8)
        label.setPixmap(QPixmap.fromImage(q_img))
        # centra l'immagine
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.on_update_graph("x=1")


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
            y = eval(self.expression, {"x": x, "np": np})
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


def set_palette(app):
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
    dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    dark_palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))
    dark_palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(127, 127, 127))

    app.setPalette(dark_palette)


def main():
    app = QApplication(sys.argv)
    set_palette(app)
    widget = GraphWidget()
    widget.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
