import os
from pathlib import Path
import yaml


BASE_DIR = Path(__file__).resolve().parent.parent
SCORING_CONFIG_PATH = BASE_DIR / "config" / "scoring.yaml"

DEFAULT_CONFIG = {
    "scoring": {
        "technical_skills": 50,
        "experience": 20,
        "education": 10,
        "projects": 10,
        "soft_skills": 10,
    }
}


def load_scoring_config() -> dict:
    """Load scoring weights from YAML config, with safe default fallback."""
    if SCORING_CONFIG_PATH.exists():
        try:
            with open(SCORING_CONFIG_PATH, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
            if isinstance(config, dict) and "scoring" in config:
                return config
        except Exception:
            pass

    # Alternative paths (e.g. Vercel deployment root)
    alt_path = Path(os.getcwd()) / "config" / "scoring.yaml"
    if alt_path.exists():
        try:
            with open(alt_path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
            if isinstance(config, dict) and "scoring" in config:
                return config
        except Exception:
            pass

    return DEFAULT_CONFIG
