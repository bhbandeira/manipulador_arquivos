import os
from datetime import datetime, timedelta
import uuid
import ffmpeg
import threading
import time

class WAVtoMP3Converter:
    def __init__(self):
        pass

    def _generate_unique_filename(self, original_name):
        """Gera um nome de arquivo único com timestamp e UUID"""
        base, ext = os.path.splitext(original_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # Pega os primeiros 8 caracteres do UUID
        return f"{base}_{timestamp}_{unique_id}{ext}"

    def convert(self, input_path, output_filename, download_folder):

        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Arquivo {input_path} não encontrado")
        
        unique_output_name = self._generate_unique_filename(output_filename)

        output_path = os.path.join(download_folder, unique_output_name)
        
        try:
            (
                ffmpeg
                .input(input_path)
                .output(output_path, acodec='libmp3lame', audio_bitrate='192k')
                .overwrite_output()
                .run(quiet=True)
            )
            
                        
            return unique_output_name
        
        except ffmpeg.Error as e:
            if os.path.exists(output_path):
                os.remove(output_path)
            raise RuntimeError(f"Erro na conversão: {e.stderr.decode('utf-8')}")
        except Exception as e:
            if os.path.exists(output_path):
                os.remove(output_path)
            raise RuntimeError(f"Erro inesperado: {str(e)}")