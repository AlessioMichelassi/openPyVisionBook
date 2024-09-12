import sys
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import numpy as np
import time


class WorkerThread(QThread):
    result_signal = pyqtSignal(np.ndarray)

    def run(self):
        print(f"Thread {self.currentThreadId()} starting computation.")
        # Operazione NumPy intensiva
        data = np.random.rand(10000, 10000)
        result = np.linalg.inv(data)
        self.result_signal.emit(result)
        print(f"Thread {self.currentThreadId()} finished computation.")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.threads = []

    def init_ui(self):
        self.button = QPushButton("Start Computation")
        self.button.clicked.connect(self.start_computation)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.setWindowTitle('PyQt, QThread, and NumPy Example')
        self.show()

    def start_computation(self):
        for i in range(4):  # Start 4 threads
            thread = WorkerThread()
            thread.result_signal.connect(self.handle_result)
            thread.start()
            self.threads.append(thread)

    def handle_result(self, result):
        print(f"Received result with shape: {result.shape}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())
