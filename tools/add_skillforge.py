
import yaml
import os

db_path = "engines/tools/tools_database.yaml"

internal_tools = {
    "skill_forge": {
        "name": "SkillForge",
        "description": "Crea dinámicamente nuevas habilidades (Skills) para Nova.",
        "keywords": ["crear skill", "nueva habilidad", "enseñar", "aprender"],
        "action_type": "script",
        "script": "tools/skill_generator.py" # Reuse the generator script
    }
}

if os.path.exists(db_path):
    with open(db_path, "r", encoding="utf-8") as f:
        db = yaml.safe_load(f) or {}
    
    if "internal_agent_tools" not in db:
        db["internal_agent_tools"] = {}
    
    db["internal_agent_tools"].update(internal_tools)
    
    with open(db_path, "w", encoding="utf-8") as f:
        yaml.dump(db, f, allow_unicode=True, default_flow_style=False)
        
    print("SkillForge agregado a las herramientas internas.")
