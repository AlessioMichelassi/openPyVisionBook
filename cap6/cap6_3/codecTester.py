import subprocess
import os
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *


class EncodingTestWorker(QThread):
    """
    Worker per eseguire il comando ffmpeg per test di codifica su diversi preset e formati.
    """
    finished = pyqtSignal(str)  # Segnale emesso quando il test è finito, con il percorso del file.
    message = pyqtSignal(str)  # Segnale per le comunicazioni da ffmpeg
    progress = pyqtSignal(int)  # Segnale per aggiornare la progress bar

    def __init__(self, input_file, output_file, ffmpeg_cmd, preset_name, duration, parent=None):
        super().__init__(parent)
        self.input_file = input_file
        self.output_file = output_file
        self.ffmpeg_cmd = ffmpeg_cmd
        self.preset_name = preset_name
        self.duration = duration

    def __del__(self):
        self.wait()

    def run(self):
        try:
            # Avvia il processo FFmpeg
            process = subprocess.Popen(self.ffmpeg_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                       text=True)

            while True:
                output = process.stderr.readline()
                if process.poll() is not None:
                    break
                if output:
                    self.message.emit(output.strip())  # Invia messaggi a QTextEdit
                    # Parsing dell'output per aggiornare la progress bar
                    if "time=" in output:
                        time_str = output.split("time=")[1].split(" ")[0]
                        time_in_seconds = self._convert_time_to_seconds(time_str)
                        progress = (time_in_seconds / self.duration) * 100
                        self.progress.emit(int(progress))

            process.communicate()  # Attendi la fine del processo

            if process.returncode == 0:
                self.finished.emit(self.output_file)
            else:
                self.message.emit(f"Errore su preset {self.preset_name}")

        except Exception as e:
            self.message.emit(f"Errore esecuzione FFmpeg: {str(e)}")

    @staticmethod
    def _convert_time_to_seconds(time_str):
        """Converte una stringa di tempo HH:MM:SS in secondi."""
        time_parts = list(map(float, time_str.split(":")))
        return time_parts[0] * 3600 + time_parts[1] * 60 + time_parts[2]


class CodecTester(QWidget):
    def __init__(self, input_file, output_dir, duration):
        super().__init__()
        self.input_file = input_file
        self.output_dir = output_dir
        self.duration = duration  # Durata del video in secondi
        self.tests = []
        self.workers = []

        # Layout principale
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Widget per messaggi
        self.text_edit = QTextEdit(self)
        self.layout.addWidget(self.text_edit)

    def add_test(self, codec_name, preset, output_format):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(self.output_dir, f"{codec_name}_{preset}_{timestamp}.{output_format}")
        ffmpeg_cmd = self.build_ffmpeg_command(self.input_file, output_file, codec_name, preset)
        self.tests.append((output_file, ffmpeg_cmd, preset))

    def build_ffmpeg_command(self, input_file, output_file, codec_name, preset):
        cmd = [
            "ffmpeg", "-y",  # Sovrascrivi file di output senza chiedere
            "-i", input_file,  # File di input
            "-pix_fmt", "yuv420p",  # Formato pixel appropriato
            "-c:v", codec_name,  # Codec video
            "-preset", preset,  # Preset (es. ultrafast, slow)
            "-b:v", "8000k",  # Bitrate massimo a 8 Mbps
            output_file
        ]
        return " ".join(cmd)

    def run_tests(self):
        for output_file, ffmpeg_cmd, preset in self.tests:
            # Crea la barra di progresso
            label = QLabel(f"Encoding {preset} - {output_file}", self)
            self.layout.addWidget(label)

            progress_bar = QProgressBar(self)
            self.layout.addWidget(progress_bar)

            # Worker per la codifica
            worker = EncodingTestWorker(self.input_file, output_file, ffmpeg_cmd, preset, self.duration)
            worker.finished.connect(self.on_test_finished)
            worker.message.connect(self.text_edit.append)  # Aggiungi messaggi a QTextEdit
            worker.progress.connect(progress_bar.setValue)  # Aggiorna la progress bar
            self.workers.append(worker)
            worker.start()

    def on_test_finished(self, output_file):
        self.text_edit.append(f"Test completato: {output_file}")
        self.workers = [w for w in self.workers if not w.isFinished()]

        if not self.workers:
            self.text_edit.append("Tutti i test sono stati completati.")


# Esempio di utilizzo
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from datetime import datetime

    app = QApplication(sys.argv)

    # Imposta input e directory di output
    input_file = r"C:\Users\aless\Videos\Netflix_TunnelFlag_4096x2160_60fps_10bit_420.y4m"
    output_dir = r"C:\Users\aless\Videos\test"
    duration = 10  # Durata del video in secondi

    tester = CodecTester(input_file, output_dir, duration)

    # Aggiungi test di codifica per H.264, H.265, AV1 con codec differenti
    tester.add_test("libx264", "slow", "mp4")
    tester.add_test("h264_nvenc", "slow", "mp4")
    tester.add_test("hevc_nvenc", "slow", "mp4")
    tester.add_test("av1_nvenc", "slow", "mkv")
    tester.add_test("h264_qsv", "slow", "mp4")
    tester.add_test("hevc_qsv", "slow", "mp4")

    # Avvia i test
    tester.run_tests()

    tester.show()
    sys.exit(app.exec())
