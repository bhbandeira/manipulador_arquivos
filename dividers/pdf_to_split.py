import os
from PyPDF2 import PdfReader, PdfWriter
from werkzeug.utils import secure_filename

class PDFtoSplitter:
    def __init__(self, upload_folder='uploads', output_folder='outputs'):
        self.upload_folder = upload_folder
        self.output_folder = output_folder
        
        
    def splitter(self, filepath, split_page):
        """Divide o PDF na página especificada"""
        try:
            # Lê o PDF original
            reader = PdfReader(filepath)
            total_pages = len(reader.pages)
            
            if split_page < 1 or split_page > total_pages:
                return None, None, "Página de divisão inválida"
            
            # Cria dois escritores para as duas partes
            writer_part1 = PdfWriter()
            writer_part2 = PdfWriter()
            
            # Divide o PDF
            for i in range(total_pages):
                if i < split_page:
                    writer_part1.add_page(reader.pages[i])
                else:
                    writer_part2.add_page(reader.pages[i])
            
            # Gera nomes de arquivo para as partes
            base_name = os.path.basename(filepath)
            name_part, ext = os.path.splitext(base_name)
            
            part1_name = f"{name_part}_part1{ext}"
            part2_name = f"{name_part}_part2{ext}"
            
            part1_path = os.path.join(self.output_folder, part1_name)
            part2_path = os.path.join(self.output_folder, part2_name)
            
            # Salva os arquivos divididos
            with open(part1_path, 'wb') as f:
                writer_part1.write(f)
            
            with open(part2_path, 'wb') as f:
                writer_part2.write(f)
            
            return part1_path, part2_path, None
        
        except Exception as e:
            return None, None, str(e)
    