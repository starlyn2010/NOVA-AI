import os
import re

class FileEngine:
    """
    Motor encargado de explorar y leer archivos locales.
    Proporciona contexto al LLM sobre el contenido de archivos.
    """
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            # Por defecto, la raíz del proyecto Nova
            self.base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        else:
            self.base_dir = base_dir
        
        # Blacklist: Nova cannot read its own code
        self.blacklist = ["core", "engines", "ui", "data", "training", "Modelfile", "orchestrator.py", "config.yaml"]

    def _is_blacklisted(self, path: str) -> bool:
        path_norm = os.path.normpath(path)
        for item in self.blacklist:
            if item in path_norm.split(os.sep):
                return True
        return False

    def process(self, query: str, health_check: bool = False) -> dict:
        if health_check:
            return {"status": "success", "message": "FileEngine ready."}
            
        query_lower = query.lower()
        read_match = re.search(r"(lee|analiza|muestra|abre|contenido|file)\s+([\w\.\-/\\_,\s]+)", query_lower)
        if read_match:
            raw_target = read_match.group(2)
            filenames = re.split(r",| y ", raw_target)
            filenames = [f.strip() for f in filenames if f.strip()]
            
            if len(filenames) > 1:
                combined_results = {}
                combined_instructions = "He analizado múltiples archivos:\n\n"
                for fname in filenames:
                    res = self.read_file(fname)
                    if res["status"] == "success":
                        combined_instructions += f"--- {fname} ---\n{res['file_content']}\n\n"
                    else:
                        combined_instructions += f"--- {fname} ---\n{res['message']}\n\n"
                
                return {
                    "status": "success",
                    "file_content": "Múltiples archivos analizados.",
                    "instructions_for_llm": combined_instructions + "Analiza estos archivos de forma conjunta para responder."
                }
            else:
                return self.read_file(filenames[0])
            
        # 2. Detectar intención de Listado
        if any(kw in query_lower for kw in ["lista", "archivos", "directorio", "qué hay", "ls", "dir"]):
            return self.list_files()

        return {
            "status": "error",
            "message": "No entendí qué quieres hacer con los archivos. Prueba con 'lista archivos' o 'lee el archivo X'."
        }

    def list_files(self, sub_dir: str = ".") -> dict:
        try:
            target_path = os.path.join(self.base_dir, sub_dir)
            if not os.path.exists(target_path):
                return {"status": "error", "message": f"La ruta {sub_dir} no existe."}
                
            items = os.listdir(target_path)
            
            # Filter blacklisted items
            files = [f for f in items if os.path.isfile(os.path.join(target_path, f)) and not self._is_blacklisted(f)]
            dirs = [d for d in items if os.path.isdir(os.path.join(target_path, d)) and not self._is_blacklisted(d)]
            
            summary = f"Archivos en {sub_dir}:\n- " + "\n- ".join(files) + f"\n\nDirectorios:\n- " + "\n- ".join(dirs)
            
            return {
                "status": "success",
                "file_list": summary,
                "instructions_for_llm": f"Aquí tienes la lista de archivos del proyecto:\n{summary}\nInforma al usuario qué archivos encontraste."
            }
        except Exception as e:
            return {"status": "error", "message": f"Error listando archivos: {str(e)}"}

    def read_file(self, filename: str) -> dict:
        try:
            # Buscar el archivo recursivamente si no se da ruta completa
            found_path = None
            for root, dirs, files in os.walk(self.base_dir):
                if filename in files:
                    found_path = os.path.join(root, filename)
                    break
            
            if not found_path:
                potential_direct = os.path.join(self.base_dir, filename)
                if os.path.exists(potential_direct) and os.path.isfile(potential_direct):
                    found_path = potential_direct

            if not found_path:
                return {"status": "error", "message": f"No pude encontrar el archivo '{filename}'."}

            abs_base = os.path.abspath(self.base_dir)
            abs_found = os.path.abspath(found_path)
            if os.path.commonpath([abs_base, abs_found]) != abs_base:
                return {"status": "error", "message": "Acceso denegado. No puedes acceder a archivos fuera del directorio de Nova."}

            if self._is_blacklisted(found_path):
                return {"status": "error", "message": "Acceso denegado. No tengo permiso para leer mis propios archivos."}

            with open(found_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            if len(content) > 5000:
                short_content = content[:5000] + "\n... (archivo truncado por tamaño) ..."
            else:
                short_content = content

            return {
                "status": "success",
                "file_content": short_content,
                "file_path": found_path,
                "instructions_for_llm": f"Contenido de '{filename}':\n\n{short_content}"
            }
        except Exception as e:
            return {"status": "error", "message": f"Error leyendo archivo '{filename}': {str(e)}"}
