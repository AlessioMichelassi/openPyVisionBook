import logging

from PyQt6.QtCore import QObject, pyqtSignal
from cap5.mainDir.outputDevice.worker.baseWorker015 import BaseWorker015
from cap5.mainDir.outputDevice.worker.baseWorker016 import BaseWorker016

logging.basicConfig(level=logging.INFO)


class StreamerManager016(QObject):
    streamWorker: BaseWorker016
    tally_SIGNAL = pyqtSignal(dict)

    def __init__(self, openGLViewer, parent=None):
        super().__init__(parent)
        self.openGLViewer = openGLViewer

    def startStreaming(self, request):
        """
        Avvia il processo di streaming con i parametri forniti nel dizionario 'request'.
        """
        ffmpeg_command = self.generateFFMpegCommand(request)
        print(f"FFmpeg command: {ffmpeg_command}")
        self.streamWorker = BaseWorker016(
            self.openGLViewer,
            ffmpeg_command,
            "Stream",
            fps=request.get('codec', {}).get('fps', 60),  # Assicurati di passare il frame rate corretto
            resolution=(1920, 1080)
        )
        self.streamWorker.tally_SIGNAL.connect(self.getTally)
        self.streamWorker.start()

    def stopStreaming(self):
        """
        Ferma il processo di streaming.
        """
        if hasattr(self, 'streamWorker') and self.streamWorker.isRunning():
            self.streamWorker.stop()
            self.streamWorker.wait()
            logging.info("Streaming worker stopped and thread joined.")

    def generateFFMpegCommandOld(self, request):
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

    def generateFFMpegCommand(self, request):
        """
        Genera il comando FFmpeg sulla base del dizionario di configurazione fornito.
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
        profile = codec.get('profile', 'high')  # YouTube consiglia 'high'
        pixel_format = codec.get('pixelFormat', 'yuv420p')
        preset = codec.get('preset', 'veryfast')
        rate_control = codec.get('rateControl', 'CBR')
        bitrate = codec.get('bitrate', 4500)  # Bitrate consigliato per 1080p60
        buffer_size = codec.get('bufferSize', 9000)
        tune = codec.get('tune', 'zerolatency')  # 'zerolatency' per streaming
        keyframe_interval = codec.get('keyframeInterval', 2)

        # Frame rate
        fps = codec.get('fps', 60)

        # Comando FFmpeg per input rawvideo tramite stdin
        command = [
            "ffmpeg", "-y",  # Sovrascrivi i file di output senza chiedere
            "-f", "rawvideo",  # Formato del video grezzo in input
            "-pixel_format", "bgr24",  # Formato pixel corrispondente a QImage convertito
            "-video_size", f"1920x1080",  # Risoluzione video
            "-framerate", f"{fps}",  # Framerate
            "-i", "-",  # Legge lo stream video da stdin
            # Aggiungi l'audio fittizio
            "-f", "lavfi",
            "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",  # Audio nullo fittizio
            "-c:v", codec_name,  # Codec video
            "-profile:v", profile,  # Profilo codec
            "-b:v", f"{bitrate}k",  # Bitrate video
            "-preset", preset,  # Preset (ultrafast, veryfast, etc.)
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
            command += ["-g", f"30"]  # Intervallo di keyframe in base al frame rate

        # Output per il flusso
        command += ["-f", "flv", f"{stream_url}/{stream_key}"]
        return command

    def getTally(self, tally_data):
        """
        Aggiorna lo stato del MixBus in base ai dati ricevuti dal TallyManager.
        """
        tally_data['sender'] = 'recManager'
        cmd = tally_data.get('cmd')
        if cmd == 'info':
            self.emitTallySignal(cmd, f"from recStream: {tally_data}")
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
