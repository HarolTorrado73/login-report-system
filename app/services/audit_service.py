"""
Auditoría empresarial.
"""

from typing import Any

from app.services.db import _get_conn, fetch_all, insert, now_iso


def log_audit(
    user_id: int | None,
    username: str | None,
    action: str,
    module: str,
    details: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> int:
    return insert(
        "audit_log",
        {
            "user_id": user_id,
            "username": username,
            "action": action,
            "module": module,
            "details": str(details or {}),
            "ip_address": ip_address or "",
            "user_agent": user_agent or "",
        },
    )


def get_audit_logs(limit: int = 200, module: str | None = None, username: str | None = None) -> list[dict[str, Any]]:
    conn = _get_conn()
    try:
        sql = "SELECT * FROM audit_log WHERE 1=1"
        params: list[Any] = []
        if module:
            sql += " AND module = ?"
            params.append(module)
        if username:
            sql += " AND username = ?"
            params.append(username)
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(int(limit))
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def export_audit_csv() -> str:
    import csv
    import io

    rows = get_audit_logs(limit=5000)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["id", "user_id", "username", "action", "module", "details", "ip_address", "created_at"])
    for r in rows:
        writer.writerow([r.get("id"), r.get("user_id"), r.get("username"), r.get("action"), r.get("module"), r.get("details"), r.get("ip_address"), r.get("created_at")])
    return buf.getvalue()
