import ffmpeg
import os
from pathlib import Path
from typing import Tuple
import uuid
from datetime import datetime

class MOVtoMP4Converter:
    def __init__(self):
        pass
    
    def _generate_output_filename(self, original_name: str) -> str:
        """Gera um nome de arquivo único para o output"""
        base = Path(original_name).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"{base}_{timestamp}_{unique_id}.mp4"

    def convert(self, input_path: str, output_name: str, output_dir: str) -> Tuple[bool, str]:
        """
        Converte MOV para MP4
        
        Args:
            input_path: Caminho completo do arquivo de entrada (str)
            output_name: Nome do arquivo de saída (sem caminho) (str)
            output_dir: Pasta de destino (str)
            
        Returns:
            Tuple (success: bool, output_path: str | error_message: str)
        """
        try:
            # Garante que output_dir é uma string
            output_dir = str(output_dir)
            output_filename = self._generate_output_filename(output_name)
            output_path = os.path.join(output_dir, output_filename)
            
            (
                ffmpeg.input(str(input_path))  # Garante que input_path é string
                .output(
                    output_path,
                    vcodec='libx264',
                    crf=23,
                    preset='fast',
                    acodec='aac',
                    movflags='+faststart'
                )
                .global_args('-loglevel', 'error')
                .run(overwrite_output=True)
            )
            
            return output_path
            
        except ffmpeg.Error as e:
            error_msg = f"Erro FFmpeg: {e.stderr.decode('utf-8').strip()}"
            return error_msg
        except Exception as e:
            return f"Erro inesperado: {str(e)}"