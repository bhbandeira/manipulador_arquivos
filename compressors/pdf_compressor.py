import os
import subprocess
from pathlib import Path
from typing import Tuple
from PIL import Image
import io
import platform
from shutil import which
from PyPDF2 import PdfReader, PdfWriter
import uuid
from datetime import datetime

class PDFCompressor:
    def __init__(self):
        self.supported_formats = ['pdf']
        self.ghostscript_path = self._find_ghostscript()

    def _generate_unique_filename(self, original_name):
        """Gera um nome de arquivo único com timestamp e UUID"""
        base, ext = os.path.splitext(original_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]  # Pega os primeiros 8 caracteres do UUID
        return f"{base}_{timestamp}_{unique_id}{ext}"

    def _find_ghostscript(self) -> str:
        """Find Ghostscript executable with Windows support"""
        if platform.system() == 'Windows':
            possible_paths = [
                r'C:\Program Files\gs\gs10.05.1\bin\gswin64c.exe',
                r'C:\Program Files\gs\gs10.05.0\bin\gswin64c.exe',
                r'C:\Program Files (x86)\gs\gs9.56.1\bin\gswin32c.exe',
                r'C:\Program Files (x86)\gs\gs9.54.0\bin\gswin32c.exe'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            
            return which('gswin64c') or which('gswin32c')
        
        return which('gs')

    def compress(self, input_path: str, output_path: str, quality: int = 50) -> Tuple[bool, str]:
        """
        Compactar um arquivo PDF usando múltiplas técnicas

        Argumentos:
        input_path: Caminho para o arquivo PDF de entrada
        output_path: Caminho para salvar o PDF compactado
        quality: Nível de qualidade da compactação (1-100)

        Retorna:
        Tupla (sucesso: bool, mensagem: str)
        """
        try:
            # First try with PyPDF2
            reader = PdfReader(input_path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            # Set compression options
            for page in writer.pages:
                for img in page.images:
                    img.replace(self._compress_image(img.data, quality))

            with open(output_path, "wb") as f:
                writer.write(f)

            # If still large, use ghostscript
            if os.path.getsize(output_path) > 50 * 1024 * 1024:  # > 50MB
                self._compress_with_ghostscript(input_path, output_path, quality)

            return True, output_path
        except Exception as e:
            try:
                # Fallback to ghostscript if PyPDF2 fails
                self._compress_with_ghostscript(input_path, output_path, quality)
                return True, output_path
            except Exception as gs_error:
                return False, f"PDF compression failed: {str(gs_error)}"

    def _compress_image(self, image_data: bytes, quality: int) -> bytes:
        """Compress an image from a PDF with PIL"""
        try:
            img = Image.open(io.BytesIO(image_data))
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality)
            return output.getvalue()
        except:
            return image_data  # Return original if compression fails

    def _compress_with_ghostscript(self, input_path: str, output_path: str, quality: int):
        """Use Ghostscript for PDF compression"""
        if not self.ghostscript_path:
            raise Exception("Ghostscript not found. Please install Ghostscript for better compression results.")

        quality_map = {
            100: '/prepress',
            75: '/printer',
            50: '/ebook',
            25: '/screen'
        }
        gs_quality = quality_map.get(quality, '/ebook')

        command = [
            self.ghostscript_path,
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            f'-dPDFSETTINGS={gs_quality}',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-sOutputFile={output_path}',
            input_path
        ]
        
        subprocess.run(command, check=True)