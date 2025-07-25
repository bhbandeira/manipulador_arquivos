import os
from pathlib import Path

# Configurações base
class Config:
    # Diretórios base
    BASE_DIR = Path(__file__).parent.parent
    
    # Upload e download
    UPLOAD_FOLDER = BASE_DIR /'uploads'
    DOWNLOAD_CONVERT_FOLDER = BASE_DIR / 'converted' / 'downloads'
    DOWNLOAD_COMPRESS_FOLDER = BASE_DIR / 'compressed' / 'downloads'  # Corrigido o nome da pasta
    
    # Limites
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024 * 1024  # 1GB
    
    # Extensões permitidas
    ALLOWED_EXTENSIONS = {
        # videos
        '3g2', '3gp', 'aaf', 'avchd', 'cavs', 'divx', 'dv', 'f4v', 'flv',
        'hevc', 'm2ts', 'm2v', 'm4v', 'mjpeg', 'mkv', 'mod', 'mpeg', 'mpeg-2',
        'mpg', 'mts', 'mxf', 'ogv', 'rm', 'rmvb', 'swf', 'tod', 'ts', 'vob',
        'webm', 'wtv', 'xvid', 'wmv', 'avi', 'asf', 'mov', 'mp4',
        # Documentos/imagens
        'pdf', 'png', 'jpg', 'jpeg',         
        # Outros                  
        'mp3','wav', 'csv', 'xlsx', 'docx'                           
    }
    
    # Configurações específicas para conversão/compressão
    VIDEO_CONVERSION_SETTINGS = {
        'output_format': 'mp4',
        'default_crf': 28
    }
    
    AUDIO_CONVERSION_SETTINGS = {
        'output_format': 'mp3',
        'bitrate': '192k'
    }

    @classmethod
    def create_folders(cls):
        """Cria todos os diretórios necessários se não existirem"""
        folders = [
            cls.UPLOAD_FOLDER,
            cls.DOWNLOAD_CONVERT_FOLDER,
            cls.DOWNLOAD_COMPRESS_FOLDER
        ]
        
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)