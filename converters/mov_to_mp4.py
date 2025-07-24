import subprocess
from datetime import datetime
import ffmpeg
import os
import uuid
import subprocess
from datetime import datetime
from pathlib import Path


class MOVtoMP4Converter:
    def __init__(self):
        pass

    
    def _generate_output_filename(self, original_name: str) -> str:
        """Gera um nome de arquivo único para o output"""
        base = Path(original_name).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"{base}_converted_{timestamp}_{unique_id}.mp4"

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