import os
import uuid
import ffmpeg
from datetime import datetime


class WMVtoMP4Converter:
    def __init__(self):
      pass

    def _generate_unique_filename(self, original_name):
        """Gera um nome de arquivo único com timestamp e UUID"""
        base, ext = os.path.splitext(original_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # Pega os primeiros 8 caracteres do UUID
        return f"{base}_{timestamp}_{unique_id}{ext}"

    def convert(self, input_path, output_filename, converted_folder):
        """Converte o arquivo WMV para MP4 usando ffmpeg-python"""

        # Gera nome único para o arquivo de saída
        unique_output_name = self._generate_unique_filename(output_filename)

        output_path = os.path.join(converted_folder, unique_output_name)
        
        try:
            (
                ffmpeg
                .input(input_path)
                .output(output_path, 
                       vcodec='libx264', 
                       acodec='aac',
                       preset='fast',
                       movflags='+faststart')
                .run(overwrite_output=True, quiet=True)
            )
            
            if not os.path.exists(output_path):
                raise RuntimeError("Arquivo de saída não foi criado")
                
            return unique_output_name
            
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode('utf8') if e.stderr else "Erro desconhecido no FFmpeg"
            self.logger.error(f"Erro na conversão: {error_msg}")
            raise RuntimeError(f"Erro na conversão: {error_msg}")
            
        except Exception as e:
            self.logger.error(f"Erro inesperado: {str(e)}")
            if os.path.exists(output_path):
                os.remove(output_path)
            raise RuntimeError(f"Falha na conversão: {str(e)}")
    