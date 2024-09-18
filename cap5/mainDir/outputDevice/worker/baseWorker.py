from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
import queue
import subprocess
import threading


class BaseWorker014(QThread):
    tally_SIGNAL = pyqtSignal(dict)

    def __init__(self, inputObject, ffmpegString, name, fps=60, resolution=(1920, 1080), parent=None):
        super().__init__(parent)
        self.inputObject = inputObject
        self.ffmpegString = ffmpegString if isinstance(ffmpegString, list) else ffmpegString.split()
        self.name = name
        self.fps = fps
        self.resolution = resolution
        self.is_working = False
        self.ffmpeg_process = None
        self.frame_queue = queue.Queue(maxsize=1200)

    def __del__(self):
        self.stop()
        self.wait()

    def run(self):
        if not self.start_ffmpeg():
            return

        # Avvia il thread per la scrittura dei frame
        threading.Thread(target=self._write_frames, daemon=True).start()

        # Cattura i frame
        self.capture_frames()

        # Ferma il processo e termina
        self.stop()

    def start_ffmpeg(self):
        """Avvia il processo FFmpeg."""
        try:
            self.ffmpeg_process = subprocess.Popen(self.ffmpegString, stdin=subprocess.PIPE)
            self.is_working = True
            self.emit_tally_signal("info", "Streaming started")
            return True
        except Exception as e:
            self.emit_tally_signal("error", f"Error starting FFmpeg: {e}")
            return False

    def capture_frames(self):
        """Cattura i frame dall'input e li mette nella coda."""
        frame_count = 0
        while self.is_working:
            frame = self.inputObject.getFrame()
            if frame is not None:
                self.enqueue_frame(frame)
            else:
                self.emit_tally_signal("warning", "Frame is None")
            frame_count += 1
            self.msleep(int(1000 / self.fps))  # Sincronizzazione del frame rate

    def enqueue_frame(self, frame):
        """Metti il frame nella coda, gestendo eventuali errori."""
        try:
            self.frame_queue.put_nowait(frame)
        except queue.Full:
            self.emit_tally_signal("warning", "Frame queue is full")

    def _write_frames(self):
        """Scrivi i frame nella stdin di FFmpeg."""
        buffer = []
        while self.is_working or not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get(timeout=1)
                buffer.append(frame)

                if len(buffer) >= 5:  # Scrive i frame in blocco
                    self.write_buffer(buffer)
            except queue.Empty:
                self.emit_tally_signal("info", "Frame queue is empty")
                continue

        # Scrivi i frame rimanenti
        if buffer:
            self.write_buffer(buffer)

    def write_buffer(self, buffer):
        """Scrive un buffer di frame nella stdin di FFmpeg."""
        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:
            try:
                self.ffmpeg_process.stdin.write(b''.join([f.tobytes() for f in buffer]))
                buffer.clear()
            except ValueError:
                self.emit_tally_signal("error", "Attempted to write to a closed file.")
                self.stop()

    def stop(self):
        """Ferma il processo di streaming e chiude FFmpeg."""
        self.is_working = False
        if self.ffmpeg_process:
            self.close_ffmpeg()

    def close_ffmpeg(self):
        """Chiude il processo FFmpeg in modo sicuro."""
        try:
            self.ffmpeg_process.stdin.close()
            self.ffmpeg_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.ffmpeg_process.kill()
            self.emit_tally_signal("error", "FFmpeg process killed after timeout")
        except Exception as e:
            self.emit_tally_signal("error", f"Error stopping FFmpeg process: {str(e)}")

    def emit_tally_signal(self, cmd, message):
        """Emette un segnale di stato per il tally."""
        tally_status = {
            'sender': f"{self.name}Worker",
            'cmd': cmd,
            'message': str(message),
        }
        self.tally_SIGNAL.emit(tally_status)
