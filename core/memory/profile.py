import json
import os

class ProfileManager:
    """
    Gestiona el perfil del usuario (nombre, preferencias, etc.)
    Persistencia en data/user_profile.json
    """
    def __init__(self, data_path: str = None):
        if data_path is None:
            # Default to ../../../data from core/memory/
            self.data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
        else:
            self.data_path = data_path
            
        self.profile_file = os.path.join(self.data_path, "user_profile.json")
        self.profile_data = {
            "name": "Usuario",
            "biography": "Usuario estándar del producto Nova.",
            "preferences": {}
        }
        self.load()

    def load(self):
        if os.path.exists(self.profile_file):
            try:
                with open(self.profile_file, "r", encoding="utf-8") as f:
                    self.profile_data = json.load(f)
            except Exception as e:
                print(f"[Profile] Error loading profile: {e}")

    def save(self):
        try:
            with open(self.profile_file, "w", encoding="utf-8") as f:
                json.dump(self.profile_data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Profile] Error saving profile: {e}")

    def get_name(self) -> str:
        return self.profile_data.get("name", "Usuario")

    def set_name(self, name: str):
        self.profile_data["name"] = name
        self.save()

    def get_preferences_string(self) -> str:
        prefs = self.profile_data.get("preferences", {})
        if not prefs:
            return ""
        return ", ".join([f"{k}: {v}" for k, v in prefs.items()])

    def update_preference(self, key: str, value: str):
        if "preferences" not in self.profile_data:
            self.profile_data["preferences"] = {}
            
        self.profile_data["preferences"][key] = value
        self.save()
