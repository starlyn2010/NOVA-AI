import os
import yaml
import re

class Skill:
    def __init__(self, name: str, path: str, metadata: dict, instructions: str):
        self.name = name
        self.path = path
        self.metadata = metadata
        self.instructions = instructions

    def __repr__(self):
        return f"<Skill {self.name} - {self.metadata.get('description', '')}>"

class SkillLoader:
    """
    Cargador modular de Habilidades (Skills) para Nova.
    Sigue el estándar de carpetas con archivos SKILL.md.
    """
    def __init__(self, skills_dir: str = None):
        if skills_dir is None:
            # Por defecto 'skills/' del proyecto
            self.skills_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "skills")
        else:
            self.skills_dir = skills_dir
        
        self.skills = {}
        self.load_all()

    def load_all(self):
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
            return

        for folder in os.listdir(self.skills_dir):
            folder_path = os.path.join(self.skills_dir, folder)
            if os.path.isdir(folder_path):
                skill_md_path = os.path.join(folder_path, "SKILL.md")
                if os.path.exists(skill_md_path):
                    skill = self._parse_skill(folder, skill_md_path)
                    if skill:
                        self.skills[folder] = skill

    def _parse_skill(self, name: str, file_path: str) -> Skill:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extraer YAML Frontmatter (si existe)
            metadata = {}
            instructions = content
            
            match = re.search(r"^---(.*?)---", content, re.DOTALL)
            if match:
                try:
                    metadata = yaml.safe_load(match.group(1))
                    instructions = content[match.end():].strip()
                except Exception:
                    pass

            return Skill(name, os.path.dirname(file_path), metadata, instructions)
        except Exception as e:
            print(f"Error cargando skill {name}: {e}")
            return None

    def get_skill_instructions(self, skill_name: str) -> str:
        skill = self.skills.get(skill_name)
        if skill:
            return f"### Skill: {skill.name}\n{skill.instructions}"
        return ""

    def list_skills(self):
        return [s.name for s in self.skills.values()]
