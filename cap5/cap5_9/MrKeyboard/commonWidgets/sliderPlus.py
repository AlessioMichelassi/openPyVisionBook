from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class SliderTextWidget(QWidget):
    def __init__(self, name, min_value=0, max_value=100, initial_value=50, parent=None):
        super(SliderTextWidget, self).__init__(parent)
        self._name = name
        self._min_value = min_value
        self._max_value = max_value
        self._initial_value = initial_value
        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        # LineEdit
        self.lineEdit = QLineEdit()
        self.lblValue = QLabel(f"{self._name}: {self._initial_value}")
        self.initUI()
        self.initConnections()
        self.initParams()

    def initUI(self):
        # Layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.lblValue)
        slide_layout = QHBoxLayout()
        slide_layout.addWidget(self.slider)
        slide_layout.addWidget(self.lineEdit)
        main_layout.addLayout(slide_layout)
        self.setLayout(main_layout)

    def initConnections(self):
        # Connections
        self.slider.valueChanged.connect(self.updateLineEdit)
        self.lineEdit.returnPressed.connect(self.updateSlider)

    def initParams(self):
        self.lineEdit.setFixedWidth(50)
        self.lineEdit.setText(str(self._initial_value))
        self.slider.setRange(self._min_value, self._max_value)
        self.slider.setValue(self._initial_value)

    def updateLineEdit(self, value):
        self.lineEdit.setText(str(value))
        self.lblValue.setText(f"{self._name}: {value} k/s")

    def updateSlider(self):
        text = self.lineEdit.text()
        if text.isdigit():
            value = int(text)
            if self.slider.minimum() <= value <= self.slider.maximum():
                self.slider.setValue(value)
            else:
                # Se il valore è fuori dal range, resetta al valore corrente dello slider
                self.lineEdit.setText(str(self.slider.value()))
        else:
            # Se il testo non è un numero valido, resetta al valore corrente dello slider
            self.lineEdit.setText(str(self.slider.value()))

    def getValue(self):
        return self.slider.value()

    def setValue(self, value):
        if self.slider.minimum() <= value <= self.slider.maximum():
            self.slider.setValue(value)
            self.lineEdit.setText(str(value))
        else:
            print(f"Il valore {value} è fuori dal range consentito.")


if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication

    app = QApplication([])
    window = SliderTextWidget("Bitrate", min_value=0, max_value=5000, initial_value=2500)
    window.show()
    app.exec()
