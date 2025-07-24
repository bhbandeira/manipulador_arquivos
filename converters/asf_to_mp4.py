import ffmpeg
import os
import uuid
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Tuple

class ASFtoMP4Converter:
    def __init__(self):
        self.supported_formats = ['asf']
    
    def _generate_output_filename(self, original_name: str) -> str:
        """Gera um nome de arquivo único para o output"""
        base = Path(original_name).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"{base}_converted_{timestamp}_{unique_id}.mp4"

    def convert(self, input_path: str, output_name: str, output_dir: str) -> Tuple[bool, str]:
        """
        Converte ASF para MP4 com FFmpeg
        
        Returns:
            Tuple (success: bool, output_path: str | error_message: str)
        """
        unique_output_name = self._generate_output_filename(output_name)

        try:
            output_path = os.path.join(output_dir, unique_output_name)
            
            (
                ffmpeg
                .input(input_path)
                .output(output_path, vcodec='libx264', acodec='aac')
                .global_args('-loglevel', 'error')  # Só mostra erros
                .run(overwrite_output=True)
            )
            
            return unique_output_name
            
        except ffmpeg.Error as e:
            error_msg = f"Erro FFmpeg: {e.stderr.decode('utf-8').strip()}"
            return False, error_msg
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"