import cv2
import numpy as np
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *

"""
This code shows how to create a pixel matrix widget 
that displays the pixel values of a video frame in real-time.
"""


class PixelMatrixWidget(QWidget):
    grid_layout_blue: QGridLayout
    grid_layout_green: QGridLayout
    grid_layout_red: QGridLayout

    lblsBlue: list[list[QLabel]]
    lblsGreen: list[list[QLabel]]
    lblsRed: list[list[QLabel]]

    lblStyle = f"""
        QLabel {{
            border: 1px solid black;
            border-radius: 2px;
            color: white;
        }}"""

    def __init__(self, video_path, grid_size=25):
        super().__init__()
        self.grid_size = grid_size
        self.single_label_size = 25
        self.video_path = video_path
        # Initialize video capture
        self.capture = cv2.VideoCapture(video_path)

        # Initialize the UI
        self.initUI()

    def initUI(self):
        mainLayout = QHBoxLayout()

        # Create three grid layouts for blue, green, and red channels
        self.grid_layout_blue = QGridLayout()
        self.grid_layout_green = QGridLayout()
        self.grid_layout_red = QGridLayout()

        # Create QLabel matrices for each channel
        self.lblsBlue = []
        self.lblsGreen = []
        self.lblsRed = []

        # Populate the grids with QLabel objects
        for i in range(self.grid_size):
            row_blue = []
            row_green = []
            row_red = []
            for j in range(self.grid_size):
                # Blue labels
                label_blue = QLabel("0")
                label_blue.setFixedSize(self.single_label_size, self.single_label_size)
                label_blue.setStyleSheet("border: 1px solid black; border-radius: 2; background-color: #0000FF; "
                                         "color: white;")
                label_blue.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label_blue.setFont(QFont("Arial", 8, QFont.Weight.Bold))
                self.grid_layout_blue.addWidget(label_blue, i, j)
                row_blue.append(label_blue)

                # Green labels
                label_green = QLabel("0")
                label_green.setFixedSize(self.single_label_size, self.single_label_size)
                label_green.setStyleSheet("border: 1px solid black; border-radius: 2;background-color: #00FF00; "
                                          "color: black;")
                label_green.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label_green.setFont(QFont("Arial", 8, QFont.Weight.Bold))
                self.grid_layout_green.addWidget(label_green, i, j)
                row_green.append(label_green)

                # Red labels
                label_red = QLabel("0")
                label_red.setFixedSize(self.single_label_size, self.single_label_size)
                label_red.setStyleSheet("border: 1px solid black; border-radius: 2;background-color: #FF0000; color: "
                                        "white;")
                label_red.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label_red.setFont(QFont("Arial", 8, QFont.Weight.Bold))
                self.grid_layout_red.addWidget(label_red, i, j)
                row_red.append(label_red)

            self.lblsBlue.append(row_blue)
            self.lblsGreen.append(row_green)
            self.lblsRed.append(row_red)

        # Add the three grids to the main layout
        mainLayout.addLayout(self.grid_layout_blue)
        mainLayout.addLayout(self.grid_layout_green)
        mainLayout.addLayout(self.grid_layout_red)

        self.setLayout(mainLayout)
        self.update_frame()

    def update_frame(self):
        ret, frame = self.capture.read()
        if not ret:
            return

        # Resize frame to the grid size (for demonstration purposes)
        resized_frame = cv2.resize(frame, (self.grid_size, self.grid_size))

        # Split channels
        b, g, r = cv2.split(resized_frame)

        # Update labels with pixel values
        self.update_labels(b, g, r)

        # Continuously update the frame
        QTimer.singleShot(30, self.update_frame)  # Adjust timing as needed

    def update_labels(self, b, g, r):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                # Update blue labels
                self.lblsBlue[i][j].setText(f"{b[i, j]}")
                # Update green labels
                self.lblsGreen[i][j].setText(f"{g[i, j]}")
                # Update red labels
                self.lblsRed[i][j].setText(f"{r[i, j]}")


def setPalette(_app):
    _app.setStyle("Fusion")
    darkPalette = QPalette()
    darkPalette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.Base, QColor(42, 42, 42))
    darkPalette.setColor(QPalette.ColorRole.AlternateBase, QColor(66, 66, 66))
    darkPalette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    darkPalette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    darkPalette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    darkPalette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(127, 127, 127))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, QColor(80, 80, 80))
    darkPalette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.HighlightedText, QColor(127, 127, 127))

    _app.setPalette(darkPalette)


if __name__ == '__main__':
    app = QApplication([])
    setPalette(app)
    video_path = r"C:\Users\aless\Videos\big_buck_bunny_1080p_h264.mov"
    ex = PixelMatrixWidget(video_path, grid_size=10)
    ex.show()
    app.exec()
