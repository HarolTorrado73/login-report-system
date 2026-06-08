"""
Autenticación empresarial con MFA TOTP y bloqueo por intentos fallidos.
"""

import os
from datetime import datetime, timedelta

from werkzeug.security import check_password_hash, generate_password_hash

from app.services.db import (
    _get_conn,
    count,
    fetch_one,
    fetch_all,
    insert,
    now_iso,
    update,
)


MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def record_login_attempt(username: str, ip_address: str | None, success: bool) -> None:
    insert("login_attempts", {
        "username": username,
        "ip_address": ip_address or "",
        "success": success,
    })


def is_locked(username: str) -> bool:
    user = fetch_one("users", {"username": username})
    if not user:
        return False
    locked_until = user.get("locked_until")
    if not locked_until:
        return False
    try:
        if datetime.utcnow() < datetime.fromisoformat(locked_until):
            return True
    except (ValueError, TypeError):
        pass
    return False


def failed_attempts_count(username: str) -> int:
    since = (datetime.utcnow() - timedelta(minutes=30)).isoformat()
    conn = _get_conn()
    try:
        row = conn.execute(
            "SELECT COUNT(*) FROM login_attempts WHERE username=? AND success=0 AND created_at > ?",
            (username, since),
        ).fetchone()
        return row[0] if row else 0
    finally:
        conn.close()


def authenticate_user(username: str, password: str, ip_address: str | None) -> dict | None:
    if is_locked(username):
        record_login_attempt(username, ip_address, False)
        return None

    user = fetch_one("users", {"username": username})
    if not user or not user.get("password_hash"):
        record_login_attempt(username, ip_address, False)
        return None

    if not check_password_hash(user["password_hash"], password):
        fails = failed_attempts_count(username) + 1
        record_login_attempt(username, ip_address, False)
        if fails >= MAX_FAILED_ATTEMPTS:
            locked_until = (datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
            update("users", {"failed_attempts": fails, "locked_until": locked_until}, {"id": user["id"]})
        else:
            update("users", {"failed_attempts": fails}, {"id": user["id"]})
        return None

    # Success
    record_login_attempt(username, ip_address, True)
    update("users", {
        "failed_attempts": 0,
        "locked_until": None,
        "last_login": now_iso(),
    }, {"id": user["id"]})
    return user


# MFA TOTP (pyotp optional)
pyotp = None
try:
    import pyotp
except Exception:
    pyotp = None


def enable_mfa(user_id: int) -> dict:
    secret = None
    if pyotp:
        secret = pyotp.random_base32()
    else:
        import secrets
        secret = secrets.token_hex(16)
    existing = fetch_one("mfa_secrets", {"user_id": user_id})
    if existing:
        update("mfa_secrets", {"secret": secret, "enabled": 1}, {"user_id": user_id})
    else:
        insert("mfa_secrets", {"user_id": user_id, "secret": secret, "enabled": 1})
    provisioning_uri = None
    if pyotp:
        user = fetch_one("users", {"id": user_id})
        username = user["username"] if user else f"user{user_id}"
        provisioning_uri = pyotp.totp.totp(secret).provisioning_uri(username, issuer_name="CyberGuard SOC")
    return {"secret": secret, "provisioning_uri": provisioning_uri}


def verify_mfa(user_id: int, code: str) -> bool:
    if not pyotp:
        return False
    row = fetch_one("mfa_secrets", {"user_id": user_id})
    if not row or not row.get("enabled") or not row.get("secret"):
        return False
    return bool(pyotp.TOTP(row["secret"]).verify(code))


def has_mfa(user_id: int) -> bool:
    row = fetch_one("mfa_secrets", {"user_id": user_id})
    return bool(row and row.get("enabled"))
