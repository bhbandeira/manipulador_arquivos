import os
import subprocess
import uuid
from datetime import datetime

class AVIToMP4Converter:
    def __init__(self):
        pass

    def _generate_unique_filename(self, original_name):
        """Gera um nome de arquivo único com timestamp e UUID"""
        base, ext = os.path.splitext(original_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # Pega os primeiros 8 caracteres do UUID
        return f"{base}_{timestamp}_{unique_id}{ext}"

    def convert(self, input_path, output_filename, converted_folder):
        """Converte o arquivo AVI para MP4 usando FFmpeg"""
        # Gera nome único para o arquivo de saída
        unique_output_name = self._generate_unique_filename(output_filename)

        output_path = os.path.join(converted_folder, unique_output_name)

        try:
            command = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-strict', 'experimental',
                '-y',
                output_path
            ]
            
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Erro FFmpeg: {result.stderr}")
            
            return unique_output_name
            
        except Exception as e:
            # Remove o arquivo de saída se a conversão falhou
            if 'output_path' in locals() and os.path.exists(output_path):
                os.remove(output_path)
            raise RuntimeError(f"Falha na conversão: {str(e)}")
    
