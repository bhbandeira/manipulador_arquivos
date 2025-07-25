import ffmpeg
import os
from pathlib import Path
from typing import Tuple

class WEBMtoMP4Converter:
    def __init__(self):
        pass
    
    def convert(self, input_path: str, output_name: str, output_dir: str) -> Tuple[bool, str]:
        """
        Converte WEBM para MP4 com FFmpeg
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_name: Nome base do arquivo de saída
            output_dir: Pasta de destino
            
        Returns:
            Tuple (success: bool, output_path: str | error_message: str)
        """
        try:
            output_path = os.path.join(output_dir, output_name)
            
            (
                ffmpeg.input(input_path)
                .output(
                    output_path,
                    vcodec='libx264',
                    preset='medium',
                    crf=23,
                    acodec='aac',
                    audio_bitrate='128k'
                )
                .global_args('-loglevel', 'error')
                .run(overwrite_output=True)
            )
            
            return output_path
            
        except ffmpeg.Error as e:
            error_msg = f"Erro FFmpeg: {e.stderr.decode('utf-8').strip()}"
            return False, error_msg
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"