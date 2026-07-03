"""Uygulama yapılandırması: yollar, ortam değişkenleri, API anahtarı deposu."""
from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("PAPERFORGE_DATA_DIR", BASE_DIR / "data"))
JOBS_DIR = DATA_DIR / "jobs"
KEYS_FILE = DATA_DIR / "keys.json"
STATIC_DIR = Path(__file__).resolve().parent / "static"

CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "paperforge@example.com")

PROVIDER_ENV = {
    "gemini": "GEMINI_API_KEY",
    "groq": "GROQ_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
}

DEFAULT_MODELS = {
    "gemini": os.environ.get("GEMINI_MODEL", "gemini-2.0-flash"),
    "groq": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
    "openrouter": os.environ.get("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
}


def is_offline() -> bool:
    return os.environ.get("PAPERFORGE_OFFLINE", "0") == "1"


def ensure_dirs() -> None:
    JOBS_DIR.mkdir(parents=True, exist_ok=True)


def _keys_from_file() -> dict[str, str]:
    if KEYS_FILE.exists():
        try:
            return {k: v for k, v in json.loads(KEYS_FILE.read_text()).items() if v}
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def get_api_keys() -> dict[str, str]:
    """Ortam değişkenleri + data/keys.json birleşimi (dosya öncelikli)."""
    keys: dict[str, str] = {}
    for provider, env_name in PROVIDER_ENV.items():
        value = os.environ.get(env_name, "").strip()
        if value:
            keys[provider] = value
    keys.update(_keys_from_file())
    return keys


def save_api_key(provider: str, key: str) -> None:
    if provider not in PROVIDER_ENV:
        raise ValueError(f"Bilinmeyen sağlayıcı: {provider}")
    ensure_dirs()
    stored = _keys_from_file()
    if key:
        stored[provider] = key.strip()
    else:
        stored.pop(provider, None)
    KEYS_FILE.write_text(json.dumps(stored, indent=2))
    try:
        os.chmod(KEYS_FILE, 0o600)
    except OSError:
        pass
