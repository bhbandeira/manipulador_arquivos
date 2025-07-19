import os
import subprocess
import logging


class MP4Compressor:
    def __init__(self,compressed_folder='compressed/downloads'):
        self.compressed_folder = compressed_folder
        
        # Configuração de logging
        self.logger = logging.getLogger(__name__)

    def compress(self, input_path, output_filename, crf):
        """Comprime o arquivo MP4 usando FFmpeg"""
        # Gera nome único para o arquivo de saída
        unique_output_name = self._generate_unique_filename(output_filename)
        
        output_path = os.path.join(self.compressed_folder, unique_output_name)
        
        try:
            command = [
                'ffmpeg',
                '-i', input_path,
                '-c:v', 'libx264',
                '-crf', str(crf),
                '-preset', 'medium',  # Mais equilibrado que 'fast'
                '-tune', 'film',      # Otimizado para conteúdo comum
                '-x264-params', 'nal-hrd=cbr:force-cfr=1',
                '-c:a', 'aac',
                '-b:a', '128k',       # Taxa de bits fixa para áudio
                '-movflags', '+faststart',
                '-threads', '2',      # Limita threads para reduzir carga
                '-y',
                output_path
            ]
            
            self.logger.info(f"Executando comando: {' '.join(command)}")
            
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
            self.logger.error(f"Erro FFmpeg: {error_msg}")
            raise RuntimeError(f"Erro na compressão: {error_msg}")
            
        except Exception as e:
            self.logger.error(f"Erro inesperado: {str(e)}")
            if os.path.exists(output_path):
                os.remove(output_path)
            raise RuntimeError(f"Falha na compressão: {str(e)}")
    