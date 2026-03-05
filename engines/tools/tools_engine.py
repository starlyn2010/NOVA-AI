import yaml
import os

class ToolsEngine:
    def __init__(self):
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.db = self._load_db()

    def _load_db(self):
        try:
            with open(os.path.join(self.base_path, "tools_database.yaml"), 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception:
            return {}

    def process(self, request: str, health_check: bool = False) -> dict:
        """
        Suggests tools OR requests execution of internal ones.
        """
        if health_check:
            return {"status": "success", "message": "ToolsEngine ready."}

        suggestions = []
        internal_actions = []
        req_lower = request.lower()
        
        # 1. Check External Tools (Suggestions only)
        for key, tool in self.db.get("tools", {}).items():
            matches = any(kw in req_lower for kw in tool.get("keywords", []))
            if matches:
                 suggestions.append(tool)
        
        # 2. Check Internal Agent Tools (Execution requests)
        for key, tool in self.db.get("internal_agent_tools", {}).items():
            matches = any(kw in req_lower for kw in tool.get("keywords", []))
            if matches:
                internal_actions.append(tool)

        # Build Response
        response = {"status": "processed"}
        
        if internal_actions:
            action = internal_actions[0] # Take first match for now
            response["action_request"] = {
                "type": action.get("action_type"),
                "script": action.get("script"),
                "name": action.get("name"),
                "description": action.get("description")
            }
            response["instructions_for_llm"] = f"Dile al usuario que puedes ejecutar: {action.get('name')}. PIDE PERMISO explícitamente."

        if suggestions:
            response["suggestions"] = suggestions
            if "instructions_for_llm" not in response:
                response["instructions_for_llm"] = "Sugiere estas herramientas técnicas al usuario."
            else:
                response["instructions_for_llm"] += " Además, sugiere estas librerías técnicas."

        if not suggestions and not internal_actions:
            return {
                "status": "no_suggestions",
                "message": "No detecté herramientas específicas."
            }

        return response
