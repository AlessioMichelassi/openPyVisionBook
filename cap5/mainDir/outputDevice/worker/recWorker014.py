import queue
import subprocess
import threading

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import numpy as np


class RecWorker014(QThread):
    tally_SIGNAL = pyqtSignal(dict)

    def __init__(self, get_frame_func, output_file="output.mp4",
                 codec="libx264", fps=60, resolution=(1920, 1080),
                 parent=None):
        super().__init__(parent)
        self.get_frame_func = get_frame_func
        self.output_file = output_file
        self.codec = codec
        self.fps = fps
        self.resolution = resolution
        self.is_recording = False
        self.ffmpeg_process = None
        self.frame_queue = queue.Queue(maxsize=1200)

    def __del__(self):
        self.stop()
        self.wait()

    def run(self):

        ffmpeg_command = [
            'ffmpeg',
            '-y',  # Sovrascrive il file se esiste
            '-hwaccel', 'cuda',  # Usa l'accelerazione hardware CUDA
            '-hwaccel_output_format', 'cuda',  # Imposta il formato di output per CUDA
            '-f', 'rawvideo',  # Formato in input
            '-vcodec', 'rawvideo',
            '-pix_fmt', 'bgr24',  # Formato pixel BGR
            '-s', '1920x1080',  # Risoluzione
            '-r', '60',  # Framerate
            '-vsync', '2',  # Sincronizzazione frame
            '-i', '-',  # Input da stdin
            '-an',  # Nessun audio
            '-c:v', 'hevc_nvenc',  # Codec video con NVENC (accelerazione CUDA)
            '-preset', 'p5',
            '-tune', 'uhq',
            '-profile:v', 'main',
            '-level', '6.2',
            '-tier', 'high',
            '-gpu', '-1',
            '-b:v', '20M',  # Bitrate massimo a 20 Mbps
            '-movflags', 'faststart',  # Moov atom inizio file
            self.output_file
        ]

        # Avvia FFmpeg
        self.ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)
        self.is_recording = True
        self.emitTallySignal("info", "Recording started")

        # Thread separato per la registrazione dei frame
        threading.Thread(target=self._write_frames, daemon=True).start()

        # Cattura i frame e mettili nella coda FIFO
        frame_count = 0
        while self.is_recording:
            frame = self.get_frame_func()
            if frame is not None:
                try:
                    self.frame_queue.put_nowait(frame)
                except queue.Full:
                    self.emitTallySignal("warning", "Frame queue is full")
            else:
                self.emitTallySignal("warning", "Frame is None")
            frame_count += 1
            self.msleep(int(1000 / self.fps))  # Sincronizzazione del frame rate

        self.ffmpeg_process.stdin.close()
        self.ffmpeg_process.wait()
        self.emitTallySignal("warning", "Recording stopped")

    def _write_frames(self):
        buffer = []
        while self.is_recording or not self.frame_queue.empty():
            try:
                frame = self.frame_queue.get(timeout=1)
                buffer.append(frame)

                # Scrive i frame in blocco
                if len(buffer) >= 10:
                    self.ffmpeg_process.stdin.write(b''.join([f.tobytes() for f in buffer]))
                    buffer.clear()
            except queue.Empty:
                self.emitTallySignal("info", "Frame queue is empty")
                continue  # Se la coda è vuota, attendi fino a quando non c'è un frame disponibile
        # Scrivi i frame rimanenti nel buffer
        if buffer:
            self.ffmpeg_process.stdin.write(b''.join([f.tobytes() for f in buffer]))

    # Se la coda è vuota, attendi fino a quando non c'è un frame disponibile

    def stop(self):
        self.is_recording = False
        self.emitTallySignal("recording", "Recording stopped")

    def emitTallySignal(self, cmd, message):
        tally_status = {
            'sender': 'recWorker',
            'cmd': cmd,
            'message': str(message),
        }
        self.tally_SIGNAL.emit(tally_status)
