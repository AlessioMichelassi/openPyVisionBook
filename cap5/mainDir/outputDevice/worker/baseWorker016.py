import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot
import subprocess
import logging
import queue
import threading

logging.basicConfig(
    level=logging.DEBUG,  # Imposta il livello di logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)


class BaseWorker016(QThread):
    # Segnale per emettere lo stato del tally
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
        self.frame_queue = queue.Queue(maxsize=60)  # Ridotto maxsize a 60
        self.quit_flag = False  # Flag per terminare il thread

    def __del__(self):
        self.stop()
        self.wait()

    def run(self):
        if not self.start_ffmpeg():
            return

        self.is_working = True

        # Avvia un thread per leggere lo stderr di FFmpeg
        self.stderr_thread = threading.Thread(target=self.read_ffmpeg_stderr, daemon=True)
        self.stderr_thread.start()

        while self.is_working and not self.quit_flag:
            frame = self.inputObject.getFrame()
            if frame is not None:
                try:
                    if frame.dtype != np.uint8 or frame.shape[2] != 3:
                        logging.warning("Frame non in formato BGR24. Convertendo...")
                        self.emit_tally_signal("warning", "Frame not in BGR24 format. Converting...")
                        frame = frame.astype(np.uint8)
                        if frame.shape[2] != 3:
                            logging.error("Frame non ha 3 canali (BGR). Scartando frame.")
                            self.emit_tally_signal("error", "Frame does not have 3 channels (BGR). Dropping frame.")
                            continue
                    self.frame_queue.put_nowait(frame)
                except queue.Full:
                    self.emit_tally_signal("warning", "Frame queue is full. Dropping frame.")
                    logging.warning("Frame queue is full. Dropping frame.")
            else:
                self.emit_tally_signal("warning", "Frame is None")
                logging.warning("Captured frame is None.")

            # Tentativo di scrivere un buffer di frame
            self.write_available_frames()

            self.msleep(int(1000 / 70))  # Mantieni il frame rate

        # Scrivi eventuali frame rimanenti
        self.write_remaining_frames()

        self.stop()
        self.stderr_thread.join()

    def start_ffmpeg(self):
        """Avvia il processo FFmpeg."""
        try:
            self.ffmpeg_process = subprocess.Popen(
                self.ffmpegString,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.is_working = True
            self.emit_tally_signal("info", "Streaming started")
            logging.info("FFmpeg process started successfully.")
            return True
        except Exception as e:
            self.emit_tally_signal("error", f"Error starting FFmpeg: {e}")
            logging.error(f"Error starting FFmpeg: {e}")
            return False

    def read_ffmpeg_stderr(self):
        """Legge e logga l'output di FFmpeg dallo stderr."""
        try:
            while True:
                if self.ffmpeg_process.stderr:
                    line = self.ffmpeg_process.stderr.readline()
                    if not line:
                        break
                    logging.debug(f"FFmpeg STDERR: {line.decode().strip()}")
                    self.emit_tally_signal("info", f"FFmpeg STDERR: {line.decode().strip()}")
        except Exception as e:
            logging.error(f"Errore nella lettura dello stderr di FFmpeg: {e}")

    def write_available_frames(self):
        """Scrive un buffer di frame nella stdin di FFmpeg."""
        buffer = []
        while len(buffer) < 5:
            try:
                frame = self.frame_queue.get_nowait()
                buffer.append(frame)
            except queue.Empty:
                break

        if buffer:
            self.write_buffer(buffer)

    def write_buffer(self, buffer):
        """Scrive un buffer di frame nella stdin di FFmpeg."""
        if self.ffmpeg_process and self.ffmpeg_process.poll() is None:
            try:
                # Assicurati che i frame siano contigui in memoria
                raw_data = b''.join([frame.tobytes() for frame in buffer])
                self.ffmpeg_process.stdin.write(raw_data)
                self.ffmpeg_process.stdin.flush()
            except Exception as e:
                self.emit_tally_signal("error", f"Error writing to FFmpeg: {e}")
                logging.error(f"Error writing to FFmpeg: {e}")
                self.stop()

    def write_remaining_frames(self):
        """Scrive tutti i frame rimanenti nella coda."""
        buffer = []
        while not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get_nowait()
                buffer.append(frame)
            except queue.Empty:
                break

            if len(buffer) >= 5:
                self.write_buffer(buffer)

        if buffer:
            self.write_buffer(buffer)

    def stop(self):
        """Ferma il processo di streaming e chiude FFmpeg."""
        if self.is_working:
            self.is_working = False
            self.quit_flag = True
            if self.ffmpeg_process:
                self.close_ffmpeg()
            self.emit_tally_signal("info", "Streaming stopped")
            logging.info("Streaming stopped.")

    def close_ffmpeg(self):
        """Chiude il processo FFmpeg in modo sicuro."""
        try:
            if self.ffmpeg_process.stdin:
                self.ffmpeg_process.stdin.close()
                logging.debug("FFmpeg stdin closed.")
            self.ffmpeg_process.wait(timeout=5)
            logging.info("FFmpeg process terminated gracefully.")
        except subprocess.TimeoutExpired:
            self.ffmpeg_process.kill()
            self.emit_tally_signal("error", "FFmpeg process killed after timeout")
            logging.error("FFmpeg process killed after timeout.")
        except Exception as e:
            self.emit_tally_signal("error", f"Error stopping FFmpeg process: {str(e)}")
            logging.error(f"Error stopping FFmpeg process: {e}")

    def emit_tally_signal(self, cmd, message):
        """Emette un segnale di stato per il tally."""
        tally_status = {
            'sender': f"{self.name}Worker",
            'cmd': cmd,
            'message': str(message),
        }
        self.tally_SIGNAL.emit(tally_status)
        logging.info(f"Tally Signal Emitted: {tally_status}")

    def quit(self):
        """Override del metodo quit per impostare il flag di uscita."""
        self.quit_flag = True
        super().quit()
        logging.info("Worker thread quit.")
