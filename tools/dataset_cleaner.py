
import json
import os

def sanitize_dataset():
    path = "knowledge/datasets/logic_core.json"
    if not os.path.exists(path):
        print("Dataset no encontrado.")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            print("Formato invalido.")
            return

        print(f"Entradas originales: {len(data)}")
        
        # Eliminar duplicados exactos usando el string del objeto como llave
        seen = set()
        clean_data = []
        for entry in data:
            entry_str = json.dumps(entry, sort_keys=True)
            if entry_str not in seen:
                # Agregar metadatos si no los tiene
                if "metadata" not in entry:
                    entry["metadata"] = {
                        "difficulty": "medium",
                        "tags": ["logic", "industrial_v3"],
                        "source": "ProjectCerebro"
                    }
                clean_data.append(entry)
                seen.add(entry_str)
        
        print(f"Entradas unicas: {len(clean_data)}")
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=4, ensure_ascii=False)
            
        print("Dataset sanitizado y guardado.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    sanitize_dataset()
