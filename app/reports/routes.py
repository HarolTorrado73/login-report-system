import csv
import io
import os

from flask import Blueprint, render_template, Response, redirect, url_for


DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "events.json")

reports = Blueprint("reports", __name__)


def _load_events():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return __import__("json").load(f)


def _get_metrics():
    events = _load_events()
    users = sorted({e.get("user") for e in events if e.get("user")})
    machines = sorted({e.get("machine") for e in events if e.get("machine")})
    logins = [e for e in events if e.get("type") == "login"]
    logouts = [e for e in events if e.get("type") == "logout"]
    return {
        "events": events,
        "users": users,
        "machines": machines,
        "total_events": len(events),
        "total_logins": len(logins),
        "total_logouts": len(logouts),
        "total_users": len(users),
        "total_machines": len(machines),
        "user_counts": {user: sum(1 for e in events if e.get("user") == user) for user in users},
        "machine_counts": {machine: sum(1 for e in events if e.get("machine") == machine) for machine in machines},
    }


@reports.route("/reports")
def reports_page():
    metrics = _get_metrics()
    return render_template("reports.html", metrics=metrics)


@reports.route("/reports/export/<kind>.<fmt>")
def export(kind, fmt):
    if fmt == "csv":
        return export_csv(kind)
    if fmt == "txt":
        return export_pdf(kind)
    return "Invalid format", 400


@reports.route("/reports/export/<kind>.csv")
def export_csv(kind):
    metrics = _get_metrics()
    buf = io.StringIO()
    writer = csv.writer(buf)
    if kind == "access":
        writer.writerow(["date", "user", "machine", "ip", "method", "type"])
        for row in metrics["events"]:
            writer.writerow([row.get("date"), row.get("user"), row.get("machine"), row.get("ip"), row.get("method"), row.get("type")])
    elif kind == "users":
        writer.writerow(["user", "events"])
        for user, count in metrics["user_counts"].items():
            writer.writerow([user, count])
    elif kind == "machines":
        writer.writerow(["machine", "events"])
        for machine, count in metrics["machine_counts"].items():
            writer.writerow([machine, count])
    else:
        return "Invalid report kind", 400
    return Response(buf.getvalue(), mimetype="text/csv", headers={"Content-Disposition": f"attachment; filename={kind}.csv"})


@reports.route("/reports/export/<kind>.txt")
def export_pdf(kind):
    metrics = _get_metrics()
    lines = [
        "CyberGuard SOC Report",
        "=" * 40,
        f"Generated: {__import__('datetime').datetime.utcnow().isoformat()}",
        f"Total events: {metrics['total_events']}",
        f"Total users: {metrics['total_users']}",
        f"Total machines: {metrics['total_machines']}",
        f"Logins: {metrics['total_logins']}",
        f"Logouts: {metrics['total_logouts']}",
    ]
    if kind == "users":
        lines.append("\nUser event counts:")
        for user, count in metrics["user_counts"].items():
            lines.append(f"- {user}: {count}")
    elif kind == "machines":
        lines.append("\nMachine event counts:")
        for machine, count in metrics["machine_counts"].items():
            lines.append(f"- {machine}: {count}")
    return "\n".join(lines), 200, {"Content-Type": "text/plain; charset=utf-8", "Content-Disposition": f"attachment; filename={kind}.txt"}
