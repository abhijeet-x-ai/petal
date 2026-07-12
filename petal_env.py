# petal_env.py
"""
Petal Environment Manager -- Load variables from .env files.
"""

import os
from pathlib import Path

def load_dotenv(project_dir=None):
    """Loads environment variables from a .env file into os.environ."""
    if project_dir is None:
        # Default to current working directory
        project_dir = Path.cwd()
    else:
        project_dir = Path(project_dir)
        
    env_path = project_dir / ".env"
    if not env_path.exists():
        return
        
    try:
        content = env_path.read_text(encoding="utf-8")
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip()
                # Strip optional quotes
                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                    val = val[1:-1]
                os.environ[key] = val
    except Exception as e:
        # Silently fail or output error
        pass
