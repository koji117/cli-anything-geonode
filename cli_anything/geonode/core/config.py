"""Connection configuration management for GeoNode CLI."""

import json
from pathlib import Path


CONFIG_DIR = Path.home() / ".cli-anything-geonode"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "url": "http://localhost:8000",
    "auth_type": "token",
    "token": None,
    "username": None,
    "password": None,
}


def _ensure_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def load_config() -> dict:
    """Load config from disk, returning defaults if not found."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE) as f:
            stored = json.load(f)
        merged = {**DEFAULT_CONFIG, **stored}
        return merged
    return dict(DEFAULT_CONFIG)


def save_config(config: dict):
    """Save config to disk."""
    _ensure_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


def set_url(url: str):
    """Set the GeoNode instance URL."""
    config = load_config()
    config["url"] = url.rstrip("/")
    save_config(config)
    return config


def set_token(token: str):
    """Set the API token."""
    config = load_config()
    config["token"] = token
    config["auth_type"] = "token"
    save_config(config)
    return config


def set_credentials(username: str, password: str):
    """Set Basic Auth credentials."""
    config = load_config()
    config["username"] = username
    config["password"] = password
    config["auth_type"] = "basic"
    save_config(config)
    return config


def show_config() -> dict:
    """Return current config with password masked."""
    config = load_config()
    display = dict(config)
    if display.get("password"):
        display["password"] = "***"
    if display.get("token"):
        t = display["token"]
        display["token"] = f"{t[:8]}...{t[-4:]}" if len(t) > 16 else "***"
    return display


def clear_config():
    """Reset config to defaults."""
    save_config(dict(DEFAULT_CONFIG))
    return DEFAULT_CONFIG
