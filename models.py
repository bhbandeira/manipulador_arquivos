import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import uuid
from converters.mkv_to_mp4 import MKVtoMP4Converter
from converters.avi_to_mp4 import AVIToMP4Converter
from converters.wmv_to_mp4 import WMVtoMP4Converter
from converters.wav_to_mp3 import WAVtoMP3Converter
from compressors.mp4_compressor import MP4Compressor
from compressors.pdf_compressor import PDFCompressor

class FileProcessor:
    """Classe principal para processamento de arquivos com suporte a múltiplos formatos e operações"""
    
    def __init__(self):
        # Inicializa todos os processadores
        self.converters = {
            'mkv': MKVtoMP4Converter(),
            'avi': AVIToMP4Converter(),
            'wmv': WMVtoMP4Converter(),
            'wav': WAVtoMP3Converter()
        }
        
        self.compressors = {
            'mp4': MP4Compressor(),
            'pdf': PDFCompressor()
        }
        
        # Mapeamento de ações para métodos
        self.action_handlers = {
            'convert': self._handle_conversion,
            'compress': self._handle_compression,
            'split_pdf': self._handle_pdf_split,
            'merge_pdf': self._handle_pdf_merge
            # Adicione novos handlers aqui
        }

    def _generate_unique_filename(self, original_name):
        """Gera um nome de arquivo único com timestamp e UUID"""
        base, ext = os.path.splitext(original_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # Pega os primeiros 8 caracteres do UUID
        return f"{base}_{timestamp}_{unique_id}{ext}"

    def get_file_summary(self, filepath: str) -> Dict[str, Any]:
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
                'compressible': False,
                'pdf_operations': []
            }
            
            # Verifica operações disponíveis por tipo de arquivo
            self._check_video_operations(filepath, file_ext, summary)
            self._check_pdf_operations(file_ext, summary)
            
            return summary
        except Exception as e:
            return {
                'error': str(e),
                'error_type': type(e).__name__
            }
    
    def _check_video_operations(self, filepath: str, file_ext: str, summary: Dict[str, Any]):
        """Verifica operações disponíveis para arquivos de vídeo"""
        if file_ext in ['mkv', 'avi', 'wmv']:
            try:
                with open(filepath, 'rb') as f:
                    header = f.read(12)
                    if (file_ext == 'wmv' and header[:4] == b'\x30\x26\xB2\x75') or \
                       (file_ext == 'mkv' and header[:4] == b'\x1A\x45\xDF\xA3') or \
                       (file_ext == 'avi' and header[:4] == b'RIFF' and header[8:12] == b'AVI '):
                        summary['convertible'] = True
                        summary['conversion_options'] = ['MP4']
            except Exception as e:
                print(f"Erro ao verificar arquivo {file_ext}: {str(e)}")
        
        if file_ext == 'mp4':
            summary['compressible'] = True
            summary['compression_options'] = ['MP4 (CRF 28)', 'MP4 (CRF 24)']
    
    def _check_pdf_operations(self, file_ext: str, summary: Dict[str, Any]):
        """Verifica operações disponíveis para PDFs"""
        if file_ext == 'pdf':
            summary['compressible'] = True
            summary['compression_options'] = [
                'PDF (Baixa qualidade)', 
                'PDF (Média qualidade)',
                'PDF (Alta qualidade)'
            ]
            summary['pdf_operations'] = [
                'Dividir PDF',
                'Juntar PDFs',
                'PDF para DOCX',
                'PDF para JPG'
            ]
    
    def handle_file_action(self, filepath: str, action: str, download_folder: str) -> Dict[str, Any]:
        """Manipula as ações solicitadas no arquivo"""
        try:
            # Extrai o tipo de ação (primeira parte antes do _)
            action_type = action.split('_')[0]
            
            # Encontra o handler apropriado
            handler = self.action_handlers.get(action_type)
            if not handler:
                return {'status': 'error', 'message': f'Tipo de ação não suportado: {action_type}'}
            
            return handler(filepath, action, download_folder)
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _handle_conversion(self, filepath: str, action: str, download_folder: str) -> Dict[str, Any]:
        """Lida com todas as operações de conversão"""
        file_ext = os.path.splitext(filepath)[1][1:].lower()
        converter = self.converters.get(file_ext)
        
        if not converter:
            return {'status': 'error', 'message': f'Conversão não suportada para .{file_ext}'}
        
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        
        if file_ext == 'wav':
            output_filename = f"{base_name}_converted.mp3"
        else:
            output_filename = f"{base_name}_converted.mp4"
        
        output_path = converter.convert(filepath, output_filename, download_folder)
        self._cleanup_original(filepath)
        
        return {
            'status': 'success',
            'message': "Conversão concluída com sucesso!",
            'download_url': f"/downloads/{os.path.basename(output_path)}"
        }
    
    def _handle_compression(self, filepath: str, action: str, download_folder: str) -> Dict[str, Any]:
        """Lida com todas as operações de compressão"""
        file_ext = os.path.splitext(filepath)[1][1:].lower()
        compressor = self.compressors.get(file_ext)
        
        if not compressor:
            return {'status': 'error', 'message': f'Compressão não suportada para .{file_ext}'}
        
        base_name = os.path.splitext(os.path.basename(filepath))[0]
        
        if file_ext == 'pdf':
            quality = self._get_pdf_quality(action)
            output_filename = f"{base_name}_compressed.pdf"
            output_filename_new = self._generate_unique_filename(output_filename)
            success, output_path = compressor.compress(filepath, os.path.join(download_folder, output_filename_new), quality)
            
            if not success:
                return {'status': 'error', 'message': output_path}  # output_path contém a mensagem de erro aqui
            
            compression_info = self._get_compression_info(filepath, output_path)
            self._cleanup_original(filepath)
            
            return {
                'status': 'success',
                'message': f"PDF comprimido com qualidade {quality}!",
                'download_url': f"/downloads/{os.path.basename(output_path)}",
                'compression_info': compression_info
            }
        else:  # MP4
            crf = int(action.split('_')[2])
            output_filename = f"{base_name}_compressed.mp4"
            output_path = compressor.compress(filepath, os.path.join(download_folder, output_filename), crf=crf)
            self._cleanup_original(filepath)
            
            return {
                'status': 'success',
                'message': f"Arquivo comprimido com CRF {crf}!",
                'download_url': f"/downloads/{os.path.basename(output_path)}"
            }
    
    def _handle_pdf_split(self, filepath: str, action: str, download_folder: str) -> Dict[str, Any]:
        """Lida com divisão de PDFs (implementação futura)"""
        # TODO: Implementar lógica de divisão de PDFs
        return {'status': 'error', 'message': 'Funcionalidade de divisão de PDFs ainda não implementada'}
    
    def _handle_pdf_merge(self, filepath: str, action: str, download_folder: str) -> Dict[str, Any]:
        """Lida com junção de PDFs (implementação futura)"""
        # TODO: Implementar lógica de junção de PDFs
        return {'status': 'error', 'message': 'Funcionalidade de junção de PDFs ainda não implementada'}
    
    def _get_pdf_quality(self, action: str) -> int:
        """Extrai a qualidade da ação de compressão de PDF"""
        if 'high' in action:
            return 75
        elif 'low' in action:
            return 25
        return 50  # padrão
    
    def _get_compression_info(self, original_path: str, compressed_path: str) -> Dict[str, str]:
        """Gera informações sobre a compressão"""
        original_size = os.path.getsize(original_path) / (1024 * 1024)  # MB
        compressed_size = os.path.getsize(compressed_path) / (1024 * 1024)
        ratio = (original_size - compressed_size) / original_size * 100
        
        return {
            'original_size': f"{original_size:.2f} MB",
            'compressed_size': f"{compressed_size:.2f} MB",
            'ratio': f"{ratio:.2f}%"
        }
    
    def _cleanup_original(self, filepath: str):
        """Remove o arquivo original após processamento"""
        try:
            os.remove(filepath)
        except Exception as e:
            print(f"AVISO: Não foi possível remover o original {filepath}: {str(e)}")

# Instância global do processador
file_processor = FileProcessor()

# Funções de interface legada (para compatibilidade)
def get_file_summary(filepath):
    return file_processor.get_file_summary(filepath)

def handle_file_action(filepath, action, download_folder):
    return file_processor.handle_file_action(filepath, action, download_folder)