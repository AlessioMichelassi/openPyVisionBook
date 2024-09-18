from PyQt6.QtCore import QObject, pyqtSignal

from cap5.mainDir.outputDevice.worker.recWorker014 import RecWorker014


class RecordingManager(QObject):
    recordingWorker: RecWorker014
    tally_SIGNAL = pyqtSignal(dict)

    def __init__(self, openGLViewer, parent=None):
        super().__init__(parent)
        self.openGLViewer = openGLViewer

    def startRecording(self, request):
        """
        Avvia il processo di streaming con i parametri forniti nel dizionario 'request'.

        :param request: Dizionario che contiene le informazioni di demuxer, codec e stream.
        """
        #ffmpeg_command = self.generateFFMpegCommand(request)
        # to do: passare ffmpeg_command a RecWorker014
        self.recordingWorker = RecWorker014(get_frame_func=self.openGLViewer.getFrame)
        self.recordingWorker.tally_SIGNAL.connect(self.getTally)
        self.recordingWorker.start()

    def stopRecording(self):
        """
        Ferma il processo di streaming.
        """
        if self.recordingWorker:
            self.recordingWorker.stop()
            self.recordingWorker.wait()
            self.emitTallySignal("stopRecording", "Recording stopped.")

    def getTally(self, tally_data):
        """
        Aggiorna lo stato del MixBus in base ai dati ricevuti dal TallyManager.
        """
        tally_data['sender'] = 'recManager'
        cmd = tally_data.get('cmd')
        if cmd == 'info':
            self.emitTallySignal(cmd, f"form recStream: {tally_data}")
        elif cmd == 'error':
            self.emitTallySignal(cmd, f"error from recStream: {tally_data}")
        elif cmd == 'warning':
            self.emitTallySignal(cmd, f"warning from recStream: {tally_data}")

    def emitTallySignal(self, cmd, message):
        tally_status = {
            'sender': 'recManager',
            'cmd': cmd,
            'message': str(message),
        }
        self.tally_SIGNAL.emit(tally_status)

    def generateFFMpegCommand(self, request):
        # Estrai informazioni dal dizionario request
        demuxer = request.get('deMuxer', {})
        codec = request.get('codec', {})
        recInfo = request.get('recInfo', {})

        # Codec settings
        codec_name = codec.get('codec', 'libx264')
        profile = codec.get('profile', 'baseline')
        pixel_format = codec.get('pixelFormat', 'yuv420p')
        preset = codec.get('preset', 'ultrafast')
        rate_control = codec.get('rateControl', 'CBR')
        bitrate = codec.get('bitrate', 2500)
        buffer_size = codec.get('bufferSize', 10000)
        tune = codec.get('tune', 'None')
        keyframe_interval = codec.get('keyframeInterval', 2)

        # Recupera il percorso completo del file dall'interfaccia RecordingInfoWidget
        output_file = recInfo.get('fileName', 'output.mp4')

        # Risoluzione dal widget OpenGLViewer
        width = 1920
        height = 1080

        # Comando FFmpeg per input rawvideo tramite stdin
        command = [
            "ffmpeg", "-y",  # Sovrascrivi i file di output senza chiedere
            "-f", "rawvideo",  # Formato del video grezzo in input
            "-pixel_format", "rgb24",  # Formato pixel corrispondente a QImage convertito
            "-video_size", f"{width}x{height}",  # Risoluzione video
            "-framerate", "60",  # Framerate di 60 fps
            "-i", "-",  # Legge lo stream video da stdin
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",  # Audio nullo fittizio
            "-c:v", codec_name,  # Codec video
            "-profile:v", profile,  # Profilo codec
            "-b:v", f"{bitrate}k",  # Bitrate video
            "-preset", preset,  # Preset (ultrafast, fast, etc.)
            "-pix_fmt", pixel_format,  # Formato pixel di output
            "-c:a", "aac",  # Codec audio
            "-b:a", "128k",  # Bitrate audio
            "-ar", "44100",  # Frequenza di campionamento audio
            "-f", "mp4", output_file  # Aggiungi l'output come file mp4
        ]

        # Opzioni avanzate
        if tune != "None":
            command += ["-tune", tune]
        if rate_control == "CBR":
            command += ["-maxrate", f"{bitrate}k"]
        if buffer_size:
            command += ["-bufsize", f"{buffer_size}k"]
        if keyframe_interval > 0:
            command += ["-g", f"{keyframe_interval * 30}"]

        return command
