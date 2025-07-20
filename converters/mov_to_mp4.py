import subprocess
from datetime import datetime
import ffmpeg



class MOVtoMP4Converter:
    def __init__(self):
        pass

    # Converte MOV para MP4 usando FFmpeg
    def convert(self, input_path, output_path):
        try:
            command = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'libx264',
                '-crf', '23',
                '-preset', 'fast',
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                '-y',
                output_path
            ]
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Erro na conversão: {e}")
            return False
        except Exception as e:
            print(f"Erro inesperado: {e}")
            return False