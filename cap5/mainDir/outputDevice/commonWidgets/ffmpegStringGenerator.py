from PyQt6.QtCore import QObject


class FFMpegStringGenerator(QObject):
    def __init__(self, parent=None):
        super(FFMpegStringGenerator, self).__init__(parent)
        self._demuxer = {}
        self._pixelFormat = ''
        self._videoSize = ''
        self._frameRate = 60
        self._stdIn = '-'
        self._codec = {}
        self._codec_name = ''
        self._stream_info = {}
        self._address = ''
        self._command = []

    def generateFFMpegCommand(self, request):
        """
        Genera la stringa di comando per FFmpeg.
        """
        # Clear the command before starting
        self._command = []

        # Aggiungi le varie componenti del comando
        self._command += self.initVideoSource(request)
        self._command += self.initAudioSource(request)
        self._command += self.initVideoCodec(request)
        self._command += self.initAudioCodec(request)
        self._command += self.addTuning(request)
        self._command += self._generateStreamCommand()

        return self._command

    def initVideoSource(self, request):
        """
        Inizializza la sorgente video.
        """
        self._pixelFormat = request.get('pixelFormat', 'bgr24')
        self._videoSize = request.get('videoSize', '1920x1080')
        self._frameRate = request.get('frameRate', 60)
        self._stdIn = request.get('stdIn', '-')

        return [
            "ffmpeg", "-y",  # Sovrascrivi file esistente
            "-f", request.get('deMuxer', 'rawvideo'),  # Formato video
            "-pixel_format", self._pixelFormat,
            "-video_size", self._videoSize,
            "-framerate", str(self._frameRate),
            "-i", self._stdIn,
        ]

    def initAudioSource(self, request):
        """
        Inizializza la sorgente audio fittizia.
        """
        return [
            "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"
        ]

    def initVideoCodec(self, request):
        """
        Inizializza il codec video.
        """
        self._codec = request.get('codec', {})
        self._codec_name = self._codec.get('codec', 'libx264')

        if self._codec_name == 'libx264':
            return self.generateLibx264Codec()
        elif self._codec_name == 'libx265':
            return self.generateLibx265Codec()
        elif self._codec_name == 'hevc_nvenc':
            return self.generateHevcNvencCodec()
        elif self._codec_name == 'h264_nvenc':
            return self.generateH264NvencCodec()
        return []

    def initAudioCodec(self, request):
        """
        Inizializza il codec audio.
        """
        return [
            "-c:a", "aac",
            "-b:a", "128k",
            "-ar", "44100"
        ]

    def addTuning(self, request):
        """
        Aggiunge opzioni di tuning avanzato come bitrate, buffer, keyframe, etc.
        """
        bitrate = self._codec.get('bitrate', 2500)
        buffer_size = self._codec.get('bufferSize', 10000)
        tune = self._codec.get('tune', 'None')
        keyframe_interval = self._codec.get('keyframeInterval', 2)

        options = [
            "-b:v", f"{bitrate}k",
            "-bufsize", f"{buffer_size}k",
        ]

        if tune and tune != 'None':
            options += ["-tune", tune]
        if keyframe_interval > 0:
            options += ["-g", str(keyframe_interval)]

        return options

    def parseStreamInfo(self, stream_info):
        """
        Memorizza le informazioni di streaming.
        """
        stream_url = stream_info.get('url', '')
        stream_key = stream_info.get('key', '')
        self._address = f"{stream_url}/{stream_key}"

    def generateLibx264Codec(self):
        """
        Genera il comando per il codec libx264.
        """
        profile = self._codec.get('profile', 'baseline')
        pixel_format = self._codec.get('pixelFormat', 'yuv420p')
        preset = self._codec.get('preset', 'ultrafast')

        return [
            "-c:v", "libx264",
            "-profile:v", profile,
            "-preset", preset,
            "-pix_fmt", pixel_format
        ]

    def generateLibx265Codec(self):
        """
        Genera il comando per il codec libx265.
        """
        profile = self._codec.get('profile', 'main')
        bitrate = self._codec.get('bitrate', 1500)

        return [
            "-c:v", "libx265",
            "-profile:v", profile,
            "-b:v", f"{bitrate}k",
            "-x265-params", "log-level=error",
            "-preset", "slow"
        ]

    def generateHevcNvencCodec(self):
        """
        Genera il comando per il codec hevc_nvenc.
        """
        preset = self._codec.get('preset', 'p5')
        if 'tune' in self._codec:
            tune = self._codec.get('tune', 'uhq')
        else:
            tune = 'hq'
        bitrate = self._codec.get('bitrate', 2500)
        profile = self._codec.get('profile', 'main')
        if 'level' in self._codec:
            level = self._codec.get('level', '6.2')
        else:
            level = '6.2'
        if 'tier' in self._codec:
            tier = self._codec.get('tier', 'high')
        else:
            tier = 'high'

        return [
            "-c:v", "hevc_nvenc",
            "-preset", preset,
            "-b:v", f"{bitrate}k",
            "-profile:v", profile,
            "-level", level,
            "-tier", tier,
            "-gpu", "-1",
            "-tune", tune
        ]

    def generateH264NvencCodec(self):
        """
        Genera il comando per il codec h264_nvenc.
        """
        preset = self._codec.get('preset', 'p5')
        bitrate = self._codec.get('bitrate', 2500)
        profile = self._codec.get('profile', 'main')

        return [
            "-c:v", "h264_nvenc",
            "-preset", preset,
            "-b:v", f"{bitrate}k",
            "-profile:v", profile
        ]

    def _generateStreamCommand(self):
        """
        Aggiunge l'indirizzo di streaming alla fine del comando.
        """
        return ["-f", "flv", self._address] if self._address else []
