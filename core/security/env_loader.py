
import os
from dotenv import load_dotenv

def load_nova_env():
    """Loads environment variables from .env file at the project root."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(project_root, ".env")
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
    
    # Pre-check critical keys (optional)
    critical_keys = [
        "GITHUB_TOKEN", 
        "NOTION_API_KEY", 
        "PIXAZO_API_KEY"
    ]
    
    found = [k for k in critical_keys if os.getenv(k)]
    print(f"[SECURITY] Nova Environment Loaded. Keys found: {len(found)}/{len(critical_keys)}")

def get_secret(key, default=None):
    """Retrieves a secret from the environment."""
    return os.getenv(key, default)
