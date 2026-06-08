"""
KPIs y métricas SOC.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from app.services.db import _get_conn, count, fetch_all


def _filter_params(**kwargs: Any):
    where = {}
    for k, v in kwargs.items():
        if v not in (None, "", [], 0):
            where[k] = v
    return where


def get_kpi_snapshot() -> dict[str, Any]:
    users_total = count("users", {})
    roles_total = count("roles", {})
    perms_total = count("permissions", {})
    machines_total = count("machines", {}) if "machines" in {} else None

    conn = _get_conn()
    try:
        events_total = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]
        logins_total = conn.execute("SELECT COUNT(*) FROM audit_log WHERE action='login'").fetchone()[0]
        logouts_total = conn.execute("SELECT COUNT(*) FROM audit_log WHERE action='logout'").fetchone()[0]
        failed_total = conn.execute("SELECT COUNT(*) FROM login_attempts WHERE success=0").fetchone()[0]
        alerts_total = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
        open_alerts = conn.execute("SELECT COUNT(*) FROM alerts WHERE status='open'").fetchone()[0]
    finally:
        conn.close()

    return {
        "users_total": users_total,
        "roles_total": roles_total,
        "permissions_total": perms_total,
        "events_total": events_total,
        "logins_total": logins_total,
        "logouts_total": logouts_total,
        "failed_total": failed_total,
        "alerts_total": alerts_total,
        "open_alerts": open_alerts,
    }


def trend_events(days: int = 7) -> dict[str, Any]:
    # Mock trend shape for charts; replace with real query if needed.
    labels = []
    values = []
    now = datetime.utcnow()
    for i in range(days):
        day = (now - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
        labels.append(day)
        values.append(0)
    return {"labels": labels, "values": values}


def threat_score() -> int:
    # Derived score from alerts severity/status and failed logins.
    conn = _get_conn()
    try:
        alerts = conn.execute(
            "SELECT severity, status FROM alerts WHERE status != 'resolved'"
        ).fetchall()
        score = 100
        weights = {"critical": 15, "high": 10, "medium": 5, "low": 2}
        for row in alerts:
            score = max(0, score - weights.get(row["severity"], 0))
        failed = conn.execute(
            "SELECT COUNT(*) FROM login_attempts WHERE success=0 AND created_at > datetime('now', '-1 day')"
        ).fetchone()[0]
        score = max(0, score - min(failed * 2, 20))
    finally:
        conn.close()
    return score


def search(query: str):
    q = (query or "").strip()
    if not q:
        return {"users": [], "machines": [], "events": [], "alerts": []}
    q_like = f"%{q}%"
    users = fetch_all("users", {"username": q_like}, order_by="id DESC", limit=20)
    machines = [{"hostname": r.get("machine", ""), "status": r.get("type", "")} for r in []]
    events = fetch_all("audit_log", {"username": q_like}, order_by="created_at DESC", limit=50)
    alerts = fetch_all("alerts", {"title": q_like}, order_by="created_at DESC", limit=50)
    return {
        "users": users,
        "machines": machines,
        "events": events,
        "alerts": alerts,
    }
