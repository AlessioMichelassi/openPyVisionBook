from PyQt6.QtCore import QObject, pyqtSignal

from cap5.mainDir.outputDevice.worker.baseWorker import BaseWorker014
from cap5.mainDir.outputDevice.worker.baseWorker015 import BaseWorker015


class StreamerManager(QObject):
    streamWorker: BaseWorker015
    tally_SIGNAL = pyqtSignal(dict)

    def __init__(self, openGLViewer, parent=None):
        super().__init__(parent)
        self.openGLViewer = openGLViewer

    def startStreaming(self, request):
        """
        Avvia il processo di streaming con i parametri forniti nel dizionario 'request'.

        :param request: Dizionario che contiene le informazioni di demuxer, codec e stream.
        """
        ffmpeg_command = self.generateFFMpegCommand(request)
        print(f"FFmpeg command: {ffmpeg_command}")
        self.streamWorker = BaseWorker015(self.openGLViewer, ffmpeg_command, "Stream")
        self.streamWorker.tally_SIGNAL.connect(self.getTally)
        self.streamWorker.start()

    def stopStreaming(self):
        """
        Ferma il processo di streaming.
        """
        if self.streamWorker:
            self.streamWorker.stop()

    def generateFFMpegCommand(self, request):
        """
        Genera il comando FFmpeg sulla base del dizionario di configurazione fornito.

        :param request: Dizionario che contiene la configurazione di demuxer, codec e streamInfo.
        :return: Stringa del comando FFmpeg.
        """
        # Estrai informazioni dal dizionario request
        demuxer = request.get('deMuxer', {})
        codec = request.get('codec', {})
        stream_info = request.get('streamInfo', {})

        # Stream URL e Stream Key
        stream_url = stream_info.get('url', '')
        stream_key = stream_info.get('key', '')

        # Codec settings
        codec_name = codec.get('codec', 'libx264')
        profile = codec.get('profile', 'baseline')
        pixel_format = codec.get('pixelFormat', 'yuv420p')
        preset = codec.get('preset', 'ultrafast')
        rate_control = codec.get('rateControl', 'CBR')
        bitrate = codec.get('bitrate', 5000)
        buffer_size = codec.get('bufferSize', 10000)
        tune = codec.get('tune', 'None')
        keyframe_interval = codec.get('keyframeInterval', 2)

        # Risoluzione dal widget OpenGLViewer
        width = 1920
        height = 1080

        # Comando FFmpeg per input rawvideo tramite stdin
        command = [
            "ffmpeg", "-y",  # Sovrascrivi i file di output senza chiedere
            "-f", "rawvideo",  # Formato del video grezzo in input
            "-pixel_format", "bgr24",  # Formato pixel corrispondente a QImage convertito
            "-video_size", f"{width}x{height}",  # Risoluzione video
            "-framerate", "60",  # Framerate di 60 fps
            "-i", "-",  # Legge lo stream video da stdin
            # Aggiungi l'audio fittizio
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
        ]

        # Aggiunta di opzioni avanzate (tune, rate control, buffer, keyframe interval)
        if tune != "None":
            command += ["-tune", tune]
        if rate_control == "CBR":
            command += ["-maxrate", f"{bitrate}k"]
        if buffer_size:
            command += ["-bufsize", f"{buffer_size}k"]
        if keyframe_interval > 0:
            command += ["-g", f"{keyframe_interval * 30}"]

        # Output per il flusso
        command += ["-f", "flv", f"{stream_url}/{stream_key}"]
        # command += ["-f", "flv", "output_test.flv"]
        return command

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
