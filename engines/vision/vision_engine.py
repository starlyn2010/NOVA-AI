import os
import re
class VisionEngine:
    """
    Motor encargado de procesar imágenes y aplicar OCR (Tesseract).
    Permite que Nova 'lea' texto de imágenes locales.
    """
    def __init__(self, tesseract_cmd: str = None):
        self.tesseract_cmd = tesseract_cmd
        if os.name == 'nt':
             self.default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        else:
             self.default_path = None

    def _get_ocr_libs(self):
        try:
            import pytesseract
            from PIL import Image
            if self.tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
            elif self.default_path and os.path.exists(self.default_path):
                pytesseract.pytesseract.tesseract_cmd = self.default_path
            return pytesseract, Image
        except ImportError:
            return None, None

    def process(self, query: str, health_check: bool = False) -> dict:
        pytesseract, Image = self._get_ocr_libs()
        if health_check:
            return {"status": "success" if pytesseract else "error", "message": "VisionEngine ready."}

        if not pytesseract:
            return {
                "status": "error",
                "message": "Librerías de OCR (pytesseract/pillow) no instaladas.",
                "instructions_for_llm": "Explica al usuario que debe instalar 'pytesseract' y 'pillow'."
            }

        query_lower = query.lower()
        img_match = re.search(r"(lee|ocr|texto|imagen|mira|extrae datos|tabla|factura)\s+([\w\.\-/\\_]+\.(png|jpg|jpeg|bmp|tiff))", query_lower)
        if img_match:
            img_path = img_match.group(2)
            is_structured = any(kw in query_lower for kw in ["datos", "tabla", "factura", "json", "estructura"])
            return self.ocr_from_image(img_path, structured=is_structured)

        return {"status": "success", "message": "Motor de visión activo. Envíe una imagen para OCR."}

    def ocr_from_image(self, img_path: str, structured: bool = False) -> dict:
        pytesseract, Image = self._get_ocr_libs()
        if not pytesseract:
            return {"status": "error", "message": "OCR no disponible."}

        try:
            if not os.path.exists(img_path):
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                potential_path = os.path.join(base_dir, img_path)
                if os.path.exists(potential_path):
                    img_path = potential_path
                else:
                    return {"status": "error", "message": f"Imagen no encontrada: {img_path}"}

            text = pytesseract.image_to_string(Image.open(img_path), lang='spa+eng')
            
            if not text.strip():
                return {
                    "status": "success",
                    "text_found": "",
                    "message": "No se detectó texto legible."
                }

            return {
                "status": "success",
                "text_found": text.strip(),
                "file_path": img_path,
                "is_structured": structured,
                "instructions_for_llm": f"Texto extraído: {text[:500]}..."
            }
        except Exception as e:
            return {"status": "error", "message": f"Error OCR: {str(e)}"}
