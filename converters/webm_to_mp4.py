import subprocess
import ffmpeg

class WEBMtoMP4Converter:
    def __init__(self):
        pass

    # Converte WEBM para MP4 usando FFmpeg
    def convert(self, input_path, output_path):
        try:
            command = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',
                '-c:a', 'aac',
                '-b:a', '128k',
                output_path
            ]
            subprocess.run(command, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erro na conversão: {e}")
            return False
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return False