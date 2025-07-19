import os
import uuid
import subprocess
from datetime import datetime


class MKVtoMP4Converter:
    def __init__(self):
        pass
    
    def _generate_unique_filename(self, original_name):
        """Gera um nome de arquivo único com timestamp e UUID"""
        base, ext = os.path.splitext(original_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # Pega os primeiros 8 caracteres do UUID
        return f"{base}_{timestamp}_{unique_id}{ext}"
    
    def convert(self, input_path, output_filename, converted_folder):
        """Converte MKV para MP4 com máxima eficiência"""

        # Gera nome único para o arquivo de saída
        unique_output_name = self._generate_unique_filename(output_filename)

        output_path = os.path.join(converted_folder, unique_output_name)
        
        try:
            # Comando otimizado - igual ao microserviço isolado
            command = [
                'ffmpeg',
                '-i', input_path,
                '-codec', 'copy',  # Copia os streams sem re-encoding
                '-movflags', '+faststart',  # Otimiza para streaming
                '-y',  # Sobrescreve sem perguntar
                output_path
            ]
            
            # Execução direta como no microserviço isolado
            process = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            if not os.path.exists(output_path):
                raise RuntimeError("Arquivo de saída não foi criado")
            
            return unique_output_name
            
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip().split('\n')[-1]
            raise RuntimeError(f"Erro FFmpeg: {error_msg}")
        except Exception as e:
            if os.path.exists(output_path):
                os.remove(output_path)
            raise RuntimeError(f"Falha na conversão: {str(e)}")
    
