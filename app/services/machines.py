import json
import os
from collections import defaultdict
from datetime import datetime


BASE_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data")
EVENTS_PATH = os.path.join(BASE_DATA, "events.json")
USERS_PATH = os.path.join(BASE_DATA, "users.json")


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _parse_time(value):
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(str(value), fmt)
        except (ValueError, TypeError):
            continue
    return None


def get_machine_stats():
    events = _load_json(EVENTS_PATH)
    users_index = {u["username"]: u for u in _load_json(USERS_PATH)}

    grouped = defaultdict(list)
    for ev in events:
        grouped[ev.get("machine")].append(ev)

    machines = []
    now = datetime.utcnow()
    for hostname, evs in grouped.items():
        evs_sorted = sorted(evs, key=lambda e: e.get("date", ""))
        active = set()
        sessions = []
        current_user = None
        last_login = None
        last_logout = None
        for ev in evs_sorted:
            if ev.get("type") == "login":
                active.add(ev.get("user"))
                current_user = ev.get("user")
                last_login = ev.get("date")
                sessions.append(
                    {
                        "user": ev.get("user"),
                        "login": ev.get("date"),
                        "logout": None,
                        "active": True,
                        "ip": ev.get("ip"),
                        "method": ev.get("method"),
                    }
                )
            elif ev.get("type") == "logout":
                active.discard(ev.get("user"))
                if current_user == ev.get("user"):
                    current_user = None
                last_logout = ev.get("date")
                for s in sessions:
                    if s["active"] and s["user"] == ev.get("user"):
                        s["logout"] = ev.get("date")
                        s["active"] = False
                        break

        risk = "Low"
        if current_user:
            risk = "Medium"
        if len([e for e in evs_sorted if e.get("type") == "login"]) >= 4:
            risk = "High"

        user = users_index.get(current_user) if current_user else None
        machine = {
            "hostname": hostname,
            "status": "Online" if current_user else "Offline",
            "user": current_user or "Unknown",
            "os": "Windows 11 Pro",
            "cpu": f"{ (hash(hostname) % 40) + 10 }%",
            "ram": f"{ (hash(hostname + 'ram') % 35) + 25 }%",
            "disk": f"{ (hash(hostname + 'disk') % 50) + 20 }%",
            "ip": evs_sorted[0].get("ip") if evs_sorted else "0.0.0.0",
            "mac": "00:1A:2B:3C:4D:5E",
            "antivirus": "Active",
            "last_connection": evs_sorted[-1].get("date") if evs_sorted else None,
            "location": "US-East",
            "risk": risk,
            "sessions": sessions,
            "email": user.get("email") if user else None,
            "role": user.get("role") if user else None,
            "last_login": last_login,
            "last_logout": last_logout,
        }
        machines.append(machine)

    machines.sort(key=lambda x: (0 if x["status"] == "Online" else 1, x["hostname"]))
    return machines


def filter_machines(machines, status=None, os_filter=None, search=None):
    result = list(machines)
    if status:
        result = [m for m in result if m["status"].lower() == status.lower()]
    if os_filter:
        result = [m for m in result if os_filter.lower() in m["os"].lower()]
    if search:
        q = search.lower()
        result = [
            m
            for m in result
            if q in m["hostname"].lower() or q in m["user"].lower() or q in m["ip"].lower()
        ]
    return result
