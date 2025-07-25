import subprocess
import os
import uuid
from datetime import datetime
from typing import Tuple

class GenericToMP4Converter:
    def __init__(self):
        self.supported_formats = [
            '3g2', '3gp', 'aaf', 'avchd', 'cavs', 'divx', 'dv', 'f4v', 'flv',
            'hevc', 'm2ts', 'm2v', 'm4v', 'mjpeg', 'mkv', 'mod', 'mpeg', 'mpeg-2',
            'mpg', 'mts', 'mxf', 'ogv', 'rm', 'rmvb', 'swf', 'tod', 'ts', 'vob',
            'webm', 'wtv', 'xvid'
        ]
    
    def _generate_output_filename(self, original_name: str) -> str:
        """Gera um nome de arquivo único para o output"""
        base = os.path.splitext(original_name)[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:8]
        return f"{base}_{timestamp}_{unique_id}.mp4"

    def detect_video_codec(self, input_path: str) -> str:
        """Detecta o codec de vídeo usando ffprobe"""
        cmd = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0',
            '-show_entries', 'stream=codec_name', '-of', 'default=nokey=1:noprint_wrappers=1',
            input_path
        ]
        try:
            return subprocess.check_output(cmd).decode('utf-8').strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erro ao detectar codec: {e.stderr.decode('utf-8')}")

    def convert(self, input_path: str, output_name: str, output_dir: str) -> Tuple[bool, str]:
        """
        Converte vídeos diversos para MP4
        
        Args:
            input_path: Caminho do arquivo de entrada
            output_name: Nome base do arquivo de saída
            output_dir: Pasta de destino
            
        Returns:
            Tuple (success: bool, output_path: str | error_message: str)
        """
        try:
            output_filename = self._generate_output_filename(output_name)
            output_path = os.path.join(output_dir, output_filename)
            
            codec = self.detect_video_codec(input_path)
            
            # Configurações base
            ffmpeg_cmd = ['ffmpeg', '-i', input_path]
            
            # Otimizações por codec
            if codec in ['h264', 'h265', 'hevc']:
                ffmpeg_cmd += ['-c:v', 'copy']  # Stream copy para codecs compatíveis
            elif codec == 'mpeg4':
                ffmpeg_cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '23']
            else:
                ffmpeg_cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', '26']
            
            # Configurações de áudio e output
            ffmpeg_cmd += [
                '-c:a', 'aac', '-b:a', '128k',
                '-movflags', '+faststart',  # Para streaming
                '-y',  # Sobrescrever se existir
                output_path
            ]
            
            subprocess.run(ffmpeg_cmd, check=True, stderr=subprocess.PIPE)
            return output_path
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Erro FFmpeg: {e.stderr.decode('utf-8')}"
            return error_msg
        except Exception as e:
            return f"Erro inesperado: {str(e)}"