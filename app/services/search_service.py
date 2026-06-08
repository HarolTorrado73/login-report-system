"""
Búsqueda global.
"""

from typing import Any

from app.services.db import fetch_all


def search(query: str) -> dict[str, Any]:
    q = (query or "").strip()
    if not q:
        return {"users": [], "machines": [], "events": [], "alerts": []}
    q_like = f"%{q}%"
    users = fetch_all("users", {"username": q_like}, order_by="id DESC", limit=20)
    events = fetch_all("audit_log", {"username": q_like}, order_by="created_at DESC", limit=50)
    alerts = fetch_all("alerts", {"title": q_like}, order_by="created_at DESC", limit=50)
    machines: list[dict[str, Any]] = []
    return {
        "users": users,
        "machines": machines,
        "events": events,
        "alerts": alerts,
    }
