import subprocess
import os


class VideoQualityMetrics:
    def __init__(self, original_video, compressed_video):
        """
        Inizializza la classe con i percorsi dei video originale e compresso.
        """
        self.original_video = original_video
        self.compressed_video = compressed_video
        self.psnr_value = None
        self.ssim_value = None
        self.vmaf_value = None

    def calculate_psnr(self):
        """
        Calcola il PSNR (Peak Signal-to-Noise Ratio) utilizzando FFmpeg.
        """
        try:
            command = [
                "ffmpeg", "-i", self.original_video, "-i", self.compressed_video,
                "-lavfi", "psnr", "-f", "null", "-"
            ]
            result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
            # Cerca PSNR nei risultati dell'output
            for line in result.stderr.splitlines():
                if "average:" in line:
                    self.psnr_value = float(line.split("average:")[1].split()[0])
                    break
            print(f"PSNR: {self.psnr_value}")
        except Exception as e:
            print(f"Errore nel calcolo del PSNR: {str(e)}")

    def calculate_ssim(self):
        """
        Calcola l'SSIM (Structural Similarity Index) utilizzando FFmpeg.
        """
        try:
            command = [
                "ffmpeg", "-i", self.original_video, "-i", self.compressed_video,
                "-lavfi", "ssim", "-f", "null", "-"
            ]
            result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
            # Cerca SSIM nei risultati dell'output
            for line in result.stderr.splitlines():
                if "All:" in line:
                    self.ssim_value = float(line.split("All:")[1].split()[0])
                    break
            print(f"SSIM: {self.ssim_value}")
        except Exception as e:
            print(f"Errore nel calcolo del SSIM: {str(e)}")

    def calculate_vmaf(self):
        """
        Calcola il VMAF (Video Multi-Method Assessment Fusion) utilizzando FFmpeg senza specificare un modello.
        """
        try:
            # Comando FFmpeg per calcolare il VMAF senza specificare il modello
            command = [
                "ffmpeg", "-i", self.original_video, "-i", self.compressed_video,
                "-lavfi", "libvmaf", "-f", "null", "-"
            ]

            # Esegui il comando e cattura sia stdout che stderr
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Analizza l'output stderr per trovare il punteggio VMAF
            found_vmaf_score = False
            for line in result.stderr.splitlines():
                if "VMAF score:" in line:
                    self.vmaf_value = float(line.split(":")[1].strip())
                    found_vmaf_score = True
                    break
                if "error" in line.lower():
                    print(f"FFmpeg error: {line}")

            if not found_vmaf_score:
                print(f"VMAF score non trovato. Ecco l'output completo di stderr:\n{result.stderr}")

            print(f"VMAF: {self.vmaf_value}")

        except Exception as e:
            # Stampa l'errore e l'output di stderr di FFmpeg
            print(f"Errore nel calcolo del VMAF: {str(e)}")
            if 'result' in locals():
                print(f"Output stderr completo di FFmpeg:\n{result.stderr}")

    def calculate_all_metrics(self):
        """
        Calcola tutti i parametri di qualità (PSNR, SSIM e VMAF).
        """
        self.calculate_psnr()
        self.calculate_ssim()
        self.calculate_vmaf()


if __name__ == "__main__":
    input_file = r"C:\Users\aless\Videos\Netflix_TunnelFlag_4096x2160_60fps_10bit_420.y4m"
    output_dir = r"C:\Users\aless\Videos\test"
    for _file in os.listdir(output_dir):
        if _file.endswith(".mp4"):
            output_file = os.path.join(output_dir, _file)
            print(f"Risultati per il video: {input_file} -> {output_file}")
            video_quality = VideoQualityMetrics(input_file, output_file)
            video_quality.calculate_all_metrics()
            print(f"PSNR: {video_quality.psnr_value}")
            print(f"SSIM: {video_quality.ssim_value}")
            print(f"VMAF: {video_quality.vmaf_value}")
