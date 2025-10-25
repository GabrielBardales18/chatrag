import os
import uuid
import re
from typing import List, Dict
import PyPDF2
from app.config import settings

class PDFProcessor:
    def __init__(self):
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        """Extrae texto de un archivo PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return text.strip()
        except Exception as e:
            raise Exception(f"Error al extraer texto del PDF: {str(e)}")
    
    def chunk_text(self, text: str) -> List[Dict[str, str]]:
        """Divide el texto en chunks para el procesamiento RAG"""
        try:
            # Limpiar el texto
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Dividir en chunks
            chunks = []
            start = 0
            
            while start < len(text):
                end = start + self.chunk_size
                
                # Si no es el último chunk, buscar un punto de corte natural
                if end < len(text):
                    # Buscar el último punto, coma o espacio dentro del chunk
                    for i in range(end, max(start + self.chunk_size // 2, end - 100), -1):
                        if text[i] in '.!?':
                            end = i + 1
                            break
                        elif text[i] in ',;':
                            end = i + 1
                            break
                        elif text[i] == ' ':
                            end = i
                            break
                
                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)
                
                # Mover el inicio con overlap
                start = end - self.chunk_overlap
                if start >= len(text):
                    break
            
            # Crear metadatos para cada chunk
            chunk_docs = []
            for i, chunk in enumerate(chunks):
                chunk_docs.append({
                    "content": chunk,
                    "metadata": {
                        "chunk_id": str(uuid.uuid4()),
                        "chunk_index": i,
                        "source": "pdf_upload"
                    }
                })
            
            return chunk_docs
        except Exception as e:
            raise Exception(f"Error al dividir el texto en chunks: {str(e)}")
    
    def process_pdf(self, file_path: str) -> Dict[str, any]:
        """Procesa un PDF completo: extrae texto y lo divide en chunks"""
        try:
            # Extraer texto
            text = self.extract_text_from_pdf(file_path)
            
            if not text.strip():
                raise Exception("El PDF no contiene texto extraíble")
            
            # Dividir en chunks
            chunks = self.chunk_text(text)
            
            return {
                "text": text,
                "chunks": chunks,
                "total_chunks": len(chunks),
                "total_characters": len(text)
            }
        except Exception as e:
            raise Exception(f"Error al procesar el PDF: {str(e)}")
    
    def validate_pdf(self, file_path: str) -> bool:
        """Valida que el archivo sea un PDF válido"""
        try:
            # Verificar extensión
            if not file_path.lower().endswith('.pdf'):
                return False
            
            # Verificar tamaño
            file_size = os.path.getsize(file_path)
            if file_size > settings.MAX_FILE_SIZE:
                return False
            
            # Verificar que sea un PDF válido
            with open(file_path, 'rb') as file:
                PyPDF2.PdfReader(file)
            
            return True
        except Exception:
            return False
