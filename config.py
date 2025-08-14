from __future__ import annotations
import os, sys
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))
try:
    exe_dir = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).parent
    env_path = exe_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=True)
except Exception:
    pass
def get_api_key() -> str:
    return os.getenv("OPENWEATHER_API_KEY", "").strip()
