import json
import os
from datetime import datetime

from app.services.report_service import generate_report


EVENTS_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "events.json")


def _normalize_event(raw):
    return {
        "date": str(raw.get("date", "")).strip(),
        "user": str(raw.get("user", "")).strip(),
        "machine": str(raw.get("machine", "")).strip(),
        "ip": str(raw.get("ip", "")).strip(),
        "method": str(raw.get("method", "")).strip(),
        "type": str(raw.get("type", "")).strip().lower(),
    }


def _load_events():
    with open(EVENTS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_events(events):
    with open(EVENTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, ensure_ascii=False, indent=4)


def _parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return None


def is_duplicate_login(events, new_event):
    machine = new_event.get("machine")
    user = new_event.get("user")
    for event in events:
        if event.get("machine") != machine:
            continue
        if event.get("user") != user:
            continue
        if event.get("type") != "logout" and event.get("date") <= new_event.get("date", ""):
            return True
    return False


def validate_event(event):
    event = _normalize_event(event)
    errors = []
    if not event["date"]:
        errors.append("date es requerido")
    if not event["user"]:
        errors.append("user es requerido")
    if not event["machine"]:
        errors.append("machine es requerido")
    if event["type"] not in {"login", "logout"}:
        errors.append("type debe ser login o logout")
    return errors, event


def get_events():
    return _load_events()


def add_event(raw_event):
    errors, event = validate_event(raw_event)
    if errors:
        return None, errors

    events = _load_events()
    if is_duplicate_login(events, event):
        return None, ["Login duplicado: el usuario ya tiene una sesion activa en esa maquina."]

    events.append(event)
    events.sort(key=lambda e: e.get("date", ""))
    _save_events(events)
    report = generate_report(events)
    return event, []
