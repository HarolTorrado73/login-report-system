import csv
import io
import json
import os
from datetime import datetime


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")
EVENTS_PATH = os.path.join(DATA_DIR, "events.json")
USERS_PATH = os.path.join(DATA_DIR, "users.json")


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_report_metrics():
    events = _load_json(EVENTS_PATH)
    users = _load_json(USERS_PATH)
    logins = [e for e in events if e.get("type") == "login"]
    logouts = [e for e in events if e.get("type") == "logout"]
    machines = sorted({e.get("machine") for e in events if e.get("machine")})
    users_online = sorted({e.get("user") for e in logins if e.get("user")})
    by_user = {}
    for e in events:
        by_user.setdefault(e.get("user", "unknown"), []).append(e)
    by_machine = {}
    for e in events:
        by_machine.setdefault(e.get("machine", "unknown"), []).append(e)
    return {
        "generated_at": datetime.utcnow().isoformat(),
        "total_events": len(events),
        "total_logins": len(logins),
        "total_logouts": len(logouts),
        "total_users": len(users),
        "total_machines": len(machines),
        "machines": machines,
        "users_online": users_online,
        "events_by_user": {k: len(v) for k, v in by_user.items()},
        "events_by_machine": {k: len(v) for k, v in by_machine.items()},
        "users": users,
        "events": events,
    }


def export_csv(metrics, kind="access"):
    buf = io.StringIO()
    writer = csv.writer(buf)
    if kind == "access":
        writer.writerow(["date", "user", "machine", "ip", "method", "type"])
        for row in metrics["events"]:
            writer.writerow([row.get("date"), row.get("user"), row.get("machine"), row.get("ip"), row.get("method"), row.get("type")])
    elif kind == "users":
        writer.writerow(["id", "username", "email", "role", "status", "created_at"])
        for row in metrics["users"]:
            writer.writerow([row.get("id"), row.get("username"), row.get("email"), row.get("role"), row.get("status"), row.get("created_at")])
    elif kind == "machines":
        writer.writerow(["machine", "events", "logins", "logouts"])
        machine_stats = {}
        for row in metrics["events"]:
            m = row.get("machine")
            machine_stats.setdefault(m, {"events": 0, "logins": 0, "logouts": 0})
            machine_stats[m]["events"] += 1
            if row.get("type") == "login":
                machine_stats[m]["logins"] += 1
            if row.get("type") == "logout":
                machine_stats[m]["logouts"] += 1
        for m, v in machine_stats.items():
            writer.writerow([m, v["events"], v["logins"], v["logouts"]])
    else:
        writer.writerow(["metric", "value"])
        for k in ["total_events", "total_logins", "total_logouts", "total_users", "total_machines"]:
            writer.writerow([k, metrics.get(k)])
    return buf.getvalue()


def export_pdf(metrics, kind="security"):
    lines = []
    lines.append("CyberGuard SOC Report")
    lines.append("=" * 40)
    lines.append(f"Generated: {metrics.get('generated_at')}")
    lines.append(f"Type: {kind}")
    lines.append("-" * 40)
    if kind == "security":
        lines.append(f"Total events: {metrics.get('total_events')}")
        lines.append(f"Logins: {metrics.get('total_logins')}")
        lines.append(f"Logouts: {metrics.get('total_logouts')}")
        lines.append(f"Users online: {', '.join(metrics.get('users_online', []))}")
        lines.append(f"Machines monitored: {', '.join(metrics.get('machines', []))}")
    else:
        lines.append(f"Total users: {metrics.get('total_users')}")
        lines.append(f"Total machines: {metrics.get('total_machines')}")
    lines.append("-" * 40)
    for user, count in metrics.get("events_by_user", {}).items():
        lines.append(f"{user}: {count}")
    return "\n".join(lines)


def export_excel(metrics, kind="access"):
    rows = []
    rows.append(["CyberGuard SOC Export"])
    rows.append([f"Generated: {metrics.get('generated_at')}"])
    rows.append([])
    if kind == "access":
        rows.append(["date", "user", "machine", "ip", "method", "type"])
        for row in metrics["events"]:
            rows.append([row.get("date"), row.get("user"), row.get("machine"), row.get("ip"), row.get("method"), row.get("type")])
    elif kind == "users":
        rows.append(["id", "username", "email", "role", "status"])
        for row in metrics["users"]:
            rows.append([row.get("id"), row.get("username"), row.get("email"), row.get("role"), row.get("status")])
    else:
        rows.append(["metric", "value"])
        for k in ["total_events", "total_logins", "total_logouts", "total_users", "total_machines"]:
            rows.append([k, metrics.get(k)])
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerows(rows)
    return buf.getvalue()
