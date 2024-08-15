from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QPushButton, QLabel


class class1(QObject):
    segnaleEseguito = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.button = QPushButton("Cliccami")
        self.button.clicked.connect(self.funzione_da_eseguire)
        self.button.show()

    def funzione_da_eseguire(self):
        print("Il pulsante è stato cliccato!")
        self.segnaleEseguito.emit()


class class2(QObject):

    def __init__(self):
        super().__init__()
        self.class1 = class1()
        self.class1.segnaleEseguito.connect(self.funzione_da_eseguire)
        self.lbl = QLabel("Aspetto il segnale")
        self.lbl.show()

    def funzione_da_eseguire(self):

        self.lbl.setText("Il segnale è stato emesso")


if __name__ == '__main__':
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window1 = class1()
    window2 = class2()
    sys.exit(app.exec())