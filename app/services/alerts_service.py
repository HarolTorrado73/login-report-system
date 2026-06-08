"""
Alertas SOC.
"""

from typing import Any

from app.services.db import _get_conn, fetch_all, fetch_one, insert, update, now_iso


def get_alerts(status: str | None = None, severity: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
    sql = "SELECT * FROM alerts WHERE 1=1"
    params: list[Any] = []
    if status:
        sql += " AND status = ?"
        params.append(status)
    if severity:
        sql += " AND severity = ?"
        params.append(severity)
    sql += " ORDER BY created_at DESC LIMIT ?"
    params.append(int(limit))
    conn = _get_conn()
    try:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_alert(alert_id: int) -> dict[str, Any] | None:
    return fetch_one("alerts", {"id": alert_id})


def create_alert(data: dict[str, Any]) -> int:
    data.setdefault("status", "open")
    data.setdefault("severity", "medium")
    data.setdefault("created_at", now_iso())
    data.setdefault("updated_at", now_iso())
    return insert("alerts", data)


def update_alert(alert_id: int, data: dict[str, Any]) -> bool:
    data["updated_at"] = now_iso()
    return update("alerts", data, {"id": alert_id})


def resolve_alert(alert_id: int, user_id: int | None = None) -> bool:
    return update(
        "alerts",
        {"status": "resolved", "resolved_at": now_iso(), "assigned_to": user_id},
        {"id": alert_id},
    )


def alert_stats() -> dict[str, int]:
    conn = _get_conn()
    try:
        total = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
        open_ = conn.execute("SELECT COUNT(*) FROM alerts WHERE status = 'open'").fetchone()[0]
        in_progress = conn.execute("SELECT COUNT(*) FROM alerts WHERE status = 'in_progress'").fetchone()[0]
        resolved = conn.execute("SELECT COUNT(*) FROM alerts WHERE status = 'resolved'").fetchone()[0]
        critical = conn.execute("SELECT COUNT(*) FROM alerts WHERE severity = 'critical' AND status != 'resolved'").fetchone()[0]
        high = conn.execute("SELECT COUNT(*) FROM alerts WHERE severity = 'high' AND status != 'resolved'").fetchone()[0]
        medium = conn.execute("SELECT COUNT(*) FROM alerts WHERE severity = 'medium' AND status != 'resolved'").fetchone()[0]
        low = conn.execute("SELECT COUNT(*) FROM alerts WHERE severity = 'low' AND status != 'resolved'").fetchone()[0]
        return {
            "total": total,
            "open": open_,
            "in_progress": in_progress,
            "resolved": resolved,
            "critical": critical,
            "high": high,
            "medium": medium,
            "low": low,
        }
    finally:
        conn.close()
