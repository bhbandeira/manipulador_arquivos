import os
import time
from datetime import datetime
from converters.mkv_to_mp4 import MKVtoMP4Converter
from converters.avi_to_mp4 import AVIToMP4Converter
from converters.wmv_to_mp4 import WMVtoMP4Converter
from compressors.mp4_compressor import MP4Compressor

# Inicializa os conversores
mkv_converter = MKVtoMP4Converter()

avi_converter = AVIToMP4Converter()

wmv_converter = WMVtoMP4Converter()

# Inicializa o compressores
mp4_compressor = MP4Compressor()

def get_file_summary(filepath):
    """Retorna um resumo das informações do arquivo"""
    try:
        stats = os.stat(filepath)
        file_ext = os.path.splitext(filepath)[1][1:].lower() or 'desconhecido'
        
        summary = {
            'filename': os.path.basename(filepath),
            'size': f"{stats.st_size / (1024 * 1024):.2f} MB",
            'created': datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            'modified': datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'type': file_ext,
            'convertible': False,
            'compressible': False
        }
        
        # Verifica se é um arquivo válido
        if file_ext in ['mkv', 'avi', 'wmv']:
            try:
                # Teste rápida para verificar se é um vídeo válido
                with open(filepath, 'rb') as f:
                    header = f.read(12)
                    # Assinaturas para MKV e AVI
                    if (file_ext == 'wmv' and header[:4] == b'\x30\x26\xB2\x75') or \
                       (file_ext == 'mkv' and header[:4] == b'\x1A\x45\xDF\xA3') or \
                       (file_ext == 'avi' and header[:4] == b'RIFF' and header[8:12] == b'AVI '):
                        summary['convertible'] = True
                        summary['conversion_options'] = ['MP4']
            except Exception as e:
                print(f"Erro ao verificar arquivo {file_ext}: {str(e)}")
        
        # Verifica se é um arquivo que pode ser comprimido (MP4)
        if file_ext == 'mp4':
            summary['compressible'] = True
            summary['compression_options'] = ['MP4 (CRF 28)', 'MP4 (CRF 24)']
        
        return summary
    except Exception as e:
        return {
            'error': str(e),
            'error_type': type(e).__name__
        }

def handle_file_action(filepath, action, download_folder):
    """Manipula as ações solicitadas no arquivo"""
    try:
        filename = os.path.basename(filepath)
        base_name = os.path.splitext(filename)[0]
        file_ext = os.path.splitext(filename)[1][1:].lower()
        
        # Ação de conversão para MP4
        if action == 'convert_to_mp4' and file_ext in ['mkv', 'avi', 'wmv']:

            if file_ext == 'mkv':
                converter = mkv_converter
                output_filename = f"{base_name}_converted.mp4"
            elif file_ext == 'avi':
                converter = avi_converter
                output_filename = f"{base_name}_converted.mp4"
            else:  # WMV
                converter = wmv_converter
                output_filename = f"{base_name}_converted.mp4"
            
            # Executa a conversão
            output_path = converter.convert(filepath, output_filename, download_folder)

            # Remove o arquivo original após conversão
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"AVISO: Não foi possível remover o original: {str(e)}")
            
            return {
                'status': 'success',
                'message': "Conversão concluída com sucesso!",
                'download_url': f"/downloads/{os.path.basename(output_path)}"
            }
        
        # Ação de comprimir arquivos MP4
        elif action.startswith('compress_mp4_'):
            crf = int(action.split('_')[2])  # Extrai o valor CRF da ação
            output_filename = f"{base_name}_compressed.mp4"
            
            output_path = mp4_compressor.compress(filepath, output_filename, crf=crf)
            
            # Remove o arquivo original após conversão
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"AVISO: Não foi possível remover o original: {str(e)}")
            
            return {
                'status': 'success',
                'message': f"Arquivo comprimido com CRF {crf}!",
                'download_url': f"/downloads/{output_path}"
            }

            
    except Exception as e:
        return {'status': 'error', 'message': str(e)}