import json

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from cap5.cap5_9.MrKeyboard.mixerKeyboard.blinkingButton import BlinkingButton
from cap5.cap5_9.MrKeyboard.styles.btnStyle import btnRedStyle


class RecordingInfoWidget(QWidget):
    fileName: QLineEdit
    btnSelectFile: QPushButton
    btnStartRecording: BlinkingButton
    txtStatus: QTextEdit
    isRecording: bool = False

    startStop_SIGNAL = pyqtSignal(str)

    def __init__(self, parent=None):
        super(RecordingInfoWidget, self).__init__(parent)
        self.initWidgets()
        self.initUI()
        self.initConnections()
        self.initStyle()

    def initWidgets(self):
        """Inizializza i widget dell'interfaccia utente."""
        self.fileName = QLineEdit("output.mp4")
        self.btnSelectFile = QPushButton("Save As...")
        self.btnStartRecording = BlinkingButton("Start Recording")
        self.txtStatus = QTextEdit()

    def initUI(self):
        """Configura il layout principale dell'interfaccia."""
        mainLayout = QVBoxLayout()

        # Etichetta per il file di output
        file_label = QLabel("Scegli il nome del file e il percorso di salvataggio:")
        mainLayout.addWidget(file_label)

        # Layout per la selezione del file di output
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.fileName)
        file_layout.addWidget(self.btnSelectFile)
        mainLayout.addLayout(file_layout)

        # Pulsante per l'avvio della registrazione
        mainLayout.addWidget(self.btnStartRecording)

        # Area di testo per gli stati e i messaggi
        mainLayout.addWidget(self.txtStatus)

        self.setLayout(mainLayout)

    def initConnections(self):
        """Connessioni tra i widget e le funzioni."""
        self.btnSelectFile.clicked.connect(self.selectFile)
        self.btnStartRecording.clicked.connect(self.startRecording)

    def initStyle(self):
        """Applica stili personalizzati ai widget."""
        self.btnStartRecording.setStyleSheet(btnRedStyle)
        self.btnStartRecording.setCheckable(True)
        self.btnSelectFile.setFixedWidth(120)  # Larghezza fissa per il pulsante "Save As..."
        self.txtStatus.setReadOnly(True)

    def startRecording(self):
        """Gestione dell'avvio e dell'interruzione della registrazione."""
        if self.isRecording:
            self.startStop_SIGNAL.emit("stopRecording")
            self.isRecording = False
            self.btnStartRecording.setText("Start Recording")
            self.txtStatus.append("Invio richiesta per fermare la registrazione.")
            self.btnStartRecording.stopBlinking()
        else:
            if not self.fileName.text():
                self.txtStatus.append("Errore: specifica un nome di file valido.")
                return

            # Invia il nome del file al RecordingManager
            self.startStop_SIGNAL.emit("startRecording")
            self.txtStatus.append(f"Inizio registrazione: {self.fileName.text()}")
            self.btnStartRecording.setText("Stop Recording")
            self.isRecording = True
            self.btnStartRecording.startBlinking()

    def selectFile(self):
        """Permette all'utente di selezionare un file (nome e cartella) per la registrazione."""
        file_dialog = QFileDialog()
        # Apri un dialogo "Salva con nome" e ottieni il percorso completo del file
        file_path, _ = file_dialog.getSaveFileName(self, "Seleziona nome e percorso del file", "", "Video Files (*.mp4);;All Files (*)")
        if file_path:
            self.fileName.setText(file_path)  # Imposta il nome del file nel QLineEdit
            self.txtStatus.append(f"Percorso di salvataggio selezionato: {file_path}")

    def getOutputFilePath(self):
        """Restituisce il percorso completo del file di registrazione."""
        return self.fileName.text()

    def clearStatus(self):
        """Pulisce l'area di stato e resetta i controlli."""
        self.txtStatus.clear()
        self.fileName.clear()
        self.isRecording = False
        self.btnStartRecording.setText("Start Recording")
        self.btnStartRecording.stopBlinking()

    def setRecordingStatus(self, isRecording: bool):
        """Imposta lo stato della registrazione e aggiorna l'interfaccia."""
        self.isRecording = isRecording
        if isRecording:
            self.btnStartRecording.setText("Stop Recording")
            self.btnStartRecording.startBlinking()
        else:
            self.btnStartRecording.setText("Start Recording")
            self.btnStartRecording.stopBlinking()

    def appendStatus(self, message: str):
        """Aggiunge un messaggio all'area di stato."""
        if isinstance(message, dict):
            # Se il messaggio è già un dizionario, estrai il contenuto.
            self.txtStatus.append(f"{message}")
        else:
            try:
                # Se il messaggio è una stringa in formato JSON, converti in dizionario.
                msg = json.loads(message)
                self.txtStatus.append(f"{msg}")
            except (json.JSONDecodeError, KeyError):
                # Se non è un JSON valido o manca qualche chiave, appendi il messaggio così com'è.
                self.txtStatus.append(message)

    def serialize(self):
        """Serializza i dati dell'interfaccia in un dizionario."""
        return {
            "fileName": self.fileName.text()
        }

    def deserialize(self, data):
        """Carica i dati serializzati nell'interfaccia utente."""
        self.fileName.setText(data["fileName"])


if __name__ == "__main__":
    app = QApplication([])
    w = RecordingInfoWidget()
    w.show()
    app.exec()
