import json
import os


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")


def _load():
    if not os.path.exists(SETTINGS_PATH):
        return {
            "general": {"org_name": "CyberGuard", "timezone": "America/Bogota", "language": "es"},
            "security": {"password_policy": "standard", "session_timeout": 30, "lockout_attempts": 5},
            "mfa": {"enabled": True, "methods": ["TOTP", "SMS"]},
            "notifications": {"email_alerts": True, "slack_webhook": "", "threshold": "medium"},
            "audit": {"retention_days": 90, "export_enabled": True},
        }
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_settings():
    return _load()


def update_settings(payload):
    data = _load()
    for section, values in payload.items():
        if section in data and isinstance(values, dict):
            data[section].update(values)
    _save(data)
    return data
