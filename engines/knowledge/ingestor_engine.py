import os
import json
from datetime import datetime

class KnowledgeIngestor:
    """
    Motor de Ingestión de Conocimiento: Extrae texto de PDFs y archivos Word
    para alimentar la memoria semántica de Nova.
    """
    def __init__(self, data_path="data"):
        self.data_path = data_path
        self.raw_path = os.path.join(data_path, "raw_documents")
        os.makedirs(self.raw_path, exist_ok=True)

    def extract_pdf(self, file_path: str) -> str:
        """Extrae texto de un archivo PDF con Lazy Load."""
        try:
            import pdfplumber
        except ImportError:
            return "Error: pdfplumber no instalado."
        
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text.strip()
        except Exception as e:
            return f"Error extrayendo PDF: {e}"

    def extract_docx(self, file_path: str) -> str:
        """Extrae texto de un archivo Word (.docx) con Lazy Load."""
        try:
            import docx
        except ImportError:
            return "Error: python-docx no instalado."
            
        try:
            doc = docx.Document(file_path)
            full_text = []
            for para in doc.paragraphs:
                full_text.append(para.text)
            return "\n".join(full_text).strip()
        except Exception as e:
            return f"Error extrayendo DOCX: {e}"

    def ingest_file(self, file_path: str) -> dict:
        """Procesa un archivo y devuelve el contenido estructurado."""
        if not os.path.exists(file_path):
            return {"status": "error", "message": "Archivo no encontrado"}

        ext = os.path.splitext(file_path)[1].lower()
        content = ""
        
        if ext == ".pdf":
            content = self.extract_pdf(file_path)
        elif ext == ".docx":
            content = self.extract_docx(file_path)
        elif ext in [".txt", ".md", ".json"]:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="latin-1") as f:
                    content = f.read()
        else:
            return {"status": "error", "message": f"Extensión no soportada: {ext}"}

        if content.startswith("Error"):
            return {"status": "error", "message": content}

        return {
            "status": "success",
            "filename": os.path.basename(file_path),
            "content": content,
            "timestamp": datetime.now().isoformat()
        }

    def process_folder(self, folder_path: str) -> list:
        """Procesa todos los archivos en una carpeta."""
        results = []
        if not os.path.isdir(folder_path):
            return results
            
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                res = self.ingest_file(full_path)
                if res["status"] == "success":
                    results.append(res)
        return results
