
import json
import os
from jsonschema import validate, ValidationError

def validate_dataset():
    path = "knowledge/datasets/logic_core.json"
    schema_path = "knowledge/datasets/logic_schema.json"
    
    if not os.path.exists(path) or not os.path.exists(schema_path):
        print("Archivos no encontrados.")
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
            
        validate(instance=data, schema=schema)
        print(f"--- VALIDACIÓN EXITOSA ---")
        print(f"Dataset '{path}' cumple con el estandar industrial v3.0.")
        
    except ValidationError as e:
        print(f"--- ERROR DE VALIDACIÓN ---")
        print(f"Ruta: {e.path}")
        print(f"Mensaje: {e.message}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    validate_dataset()
