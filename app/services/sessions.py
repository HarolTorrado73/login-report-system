import json
import os
from datetime import datetime


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
EVENTS_PATH = os.path.join(DATA_DIR, "events.json")
SETTINGS_PATH = os.path.join(DATA_DIR, "settings.json")


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _parse_time(value):
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(str(value), fmt)
        except (ValueError, TypeError):
            continue
    return None


def get_sessions():
    events = _load_json(EVENTS_PATH)
    sessions = []
    active_by_user_machine = {}
    for ev in events:
        key = (ev.get("user"), ev.get("machine"))
        if ev.get("type") == "login":
            active_by_user_machine[key] = {
                "user": ev.get("user"),
                "machine": ev.get("machine"),
                "login_time": ev.get("date"),
                "logout_time": None,
                "ip": ev.get("ip"),
                "method": ev.get("method"),
                "mfa": "Enabled" if ev.get("method") in ("MFA", "SSO") else "Disabled",
                "active": True,
            }
        elif ev.get("type") == "logout":
            if key in active_by_user_machine:
                active_by_user_machine[key]["logout_time"] = ev.get("date")
                active_by_user_machine[key]["active"] = False
                sessions.append(active_by_user_machine.pop(key))
    for s in active_by_user_machine.values():
        sessions.append(s)
    for s in sessions:
        login = _parse_time(s["login_time"])
        logout = _parse_time(s["logout_time"]) or datetime.utcnow()
        if login:
            s["duration"] = round((logout - login).total_seconds() / 60.0, 1)
        else:
            s["duration"] = 0
    sessions.sort(key=lambda x: x["login_time"] or "", reverse=True)
    return sessions


def terminate_session(user, machine):
    events = _load_json(EVENTS_PATH)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    for ev in reversed(events):
        if ev.get("user") == user and ev.get("machine") == machine and ev.get("type") == "login":
            events.append({
                "date": now,
                "user": user,
                "machine": machine,
                "ip": ev.get("ip", "0.0.0.0"),
                "method": ev.get("method", "Local"),
                "type": "logout",
            })
            _save_json(EVENTS_PATH, events)
            return True
    return False
