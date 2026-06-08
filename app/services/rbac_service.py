"""
RBAC empresarial.
"""

from typing import Any

from app.services.db import _get_conn, fetch_all, fetch_one, insert


def get_user_permissions(user_id: int) -> list[str]:
    conn = _get_conn()
    try:
        row = conn.execute(
            """SELECT p.code
               FROM permissions p
               JOIN user_roles ur ON ur.role_id = roles.id
               JOIN roles ON roles.id = ur.role_id
               WHERE ur.user_id = ?""",
            (user_id,),
        ).fetchone()
        if not row:
            return []
        codes = [c.strip() for c in row[0].strip("[]").replace('"', "").split(",") if c.strip()] if row[0] else []
        return codes
    finally:
        conn.close()


def user_can(user_id: int, permission: str) -> bool:
    if not user_id:
        return False
    perms = get_user_permissions(user_id)
    return "*" in perms or permission in perms


def get_roles() -> list[dict[str, Any]]:
    return fetch_all("roles", order_by="name ASC")


def get_permissions() -> list[dict[str, Any]]:
    return fetch_all("permissions", order_by="module ASC, code ASC")


def assign_role(user_id: int, role_id: int) -> None:
    insert("user_roles", {"user_id": user_id, "role_id": role_id})


def get_user_roles(user_id: int) -> list[dict[str, Any]]:
    conn = _get_conn()
    try:
        rows = conn.execute(
            """SELECT r.*
               FROM roles r
               JOIN user_roles ur ON ur.role_id = r.id
               WHERE ur.user_id = ?""",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()
