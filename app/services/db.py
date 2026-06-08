"""
Enterprise database layer for CyberGuard SOC.
SQLite-backed with JSON compatibility layer.
"""

import json
import os
import sqlite3
from datetime import datetime
from typing import Any


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cyberguard.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'viewer',
    status TEXT DEFAULT 'active',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_login TEXT,
    failed_attempts INTEGER DEFAULT 0,
    locked_until TEXT
);

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT DEFAULT '[]',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER,
    role_id INTEGER,
    assigned_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    module TEXT NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    action TEXT NOT NULL,
    module TEXT NOT NULL,
    details TEXT,
    ip_address TEXT,
    user_agent TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    severity TEXT DEFAULT 'medium',
    status TEXT DEFAULT 'open',
    title TEXT NOT NULL,
    description TEXT,
    machine TEXT,
    user TEXT,
    ip_address TEXT,
    assigned_to INTEGER,
    resolved_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    module TEXT DEFAULT 'general',
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS login_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    ip_address TEXT,
    success BOOLEAN DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mfa_secrets (
    user_id INTEGER PRIMARY KEY,
    secret TEXT,
    enabled BOOLEAN DEFAULT 0,
    backup_codes TEXT DEFAULT '[]',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_audit_log_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_created ON audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_login_attempts_user ON login_attempts(username);
"""

SEED_ROLES = [
    ("admin", "Administrador del sistema", '["*"]'),
    ("analyst", "Analista de seguridad", '["machines:read", "sessions:read", "reports:read", "alerts:read", "alerts:write"]'),
    ("viewer", "Solo lectura", '["dashboard:read", "machines:read", "sessions:read", "reports:read"]'),
]

SEED_PERMISSIONS = [
    ("dashboard:read", "Ver dashboard", "dashboard"),
    ("machines:read", "Ver máquinas", "machines"),
    ("machines:write", "Editar máquinas", "machines"),
    ("sessions:read", "Ver sesiones", "sessions"),
    ("sessions:terminate", "Terminar sesiones", "sessions"),
    ("reports:read", "Ver reportes", "reports"),
    ("reports:export", "Exportar reportes", "reports"),
    ("alerts:read", "Ver alertas", "alerts"),
    ("alerts:write", "Gestionar alertas", "alerts"),
    ("alerts:resolve", "Resolver alertas", "alerts"),
    ("settings:read", "Ver configuración", "settings"),
    ("settings:write", "Modificar configuración", "settings"),
    ("users:read", "Ver usuarios", "users"),
    ("users:write", "Gestionar usuarios", "users"),
    ("roles:read", "Ver roles", "roles"),
    ("roles:write", "Gestionar roles", "roles"),
]


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(seed: bool = True):
    """Create tables and optional seed data."""
    conn = _get_conn()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
        if seed:
            _seed(conn)
    finally:
        conn.close()


def _seed(conn: sqlite3.Connection):
    """Seed initial data if not present."""
    for role_name, description, permissions in SEED_ROLES:
        conn.execute(
            "INSERT OR IGNORE INTO roles (name, description, permissions) VALUES (?, ?, ?)",
            (role_name, description, permissions),
        )
    for code, name, module in SEED_PERMISSIONS:
        conn.execute(
            "INSERT OR IGNORE INTO permissions (code, name, module) VALUES (?, ?, ?)",
            (code, name, module),
        )
    conn.commit()


def now_iso() -> str:
    return datetime.utcnow().isoformat()


# ------------------------------
# Generic helpers
# ------------------------------

def insert(table: str, data: dict) -> int:
    conn = _get_conn()
    try:
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        cur = conn.execute(sql, tuple(data.values()))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update(table: str, data: dict, where: dict) -> bool:
    conn = _get_conn()
    try:
        set_clause = ", ".join([f"{k}=?" for k in data.keys()])
        where_clause = " AND ".join([f"{k}=?" for k in where.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        conn.execute(sql, tuple(data.values()) + tuple(where.values()))
        conn.commit()
        return True
    finally:
        conn.close()


def delete(table: str, where: dict) -> bool:
    conn = _get_conn()
    try:
        where_clause = " AND ".join([f"{k}=?" for k in where.keys()])
        sql = f"DELETE FROM {table} WHERE {where_clause}"
        conn.execute(sql, tuple(where.values()))
        conn.commit()
        return True
    finally:
        conn.close()


def fetch_one(table: str, where: dict) -> dict | None:
    conn = _get_conn()
    try:
        where_clause = " AND ".join([f"{k}=?" for k in where.keys()])
        sql = f"SELECT * FROM {table} WHERE {where_clause} LIMIT 1"
        row = conn.execute(sql, tuple(where.values())).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def fetch_all(table: str, where: dict | None = None, order_by: str = "id DESC", limit: int | None = None) -> list[dict]:
    conn = _get_conn()
    try:
        sql = f"SELECT * FROM {table}"
        params: tuple[Any, ...] = ()
        if where:
            where_clause = " AND ".join([f"{k}=?" for k in where.keys()])
            sql += f" WHERE {where_clause}"
            params = tuple(where.values())
        sql += f" ORDER BY {order_by}"
        if limit:
            sql += f" LIMIT {int(limit)}"
        return [dict(r) for r in conn.execute(sql, params).fetchall()]
    finally:
        conn.close()


def count(table: str, where: dict | None = None) -> int:
    conn = _get_conn()
    try:
        sql = f"SELECT COUNT(*) FROM {table}"
        params: tuple[Any, ...] = ()
        if where:
            where_clause = " AND ".join([f"{k}=?" for k in where.keys()])
            sql += f" WHERE {where_clause}"
            params = tuple(where.values())
        return conn.execute(sql, params).fetchone()[0]
    finally:
        conn.close()


# ------------------------------
# JSON compatibility layer
# ------------------------------

def json_path(*parts: str) -> str:
    return os.path.join(os.path.dirname(__file__), "..", "..", "data", *parts)


def load_json(path: str) -> Any:
    full = json_path(path)
    if not os.path.exists(full):
        return []
    with open(full, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Any) -> None:
    full = json_path(path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def migrate_json_to_sql():
    """Best-effort migration from JSON files to SQLite."""
    if not os.path.exists(DB_PATH):
        init_db(seed=True)

    # Migrate users from users.json
    users_json = load_json("users.json")
    if users_json:
        conn = _get_conn()
        try:
            for u in users_json:
                conn.execute(
                    """INSERT OR IGNORE INTO users
                       (id, username, email, password_hash, role, status, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        u.get("id"),
                        u.get("username"),
                        u.get("email"),
                        u.get("password_hash"),
                        u.get("role", "viewer"),
                        u.get("status", "active"),
                        u.get("created_at", now_iso()),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

    # Migrate events into audit_log
    events = load_json("events.json")
    if events:
        conn = _get_conn()
        try:
            for ev in events:
                conn.execute(
                    """INSERT OR IGNORE INTO audit_log
                       (username, action, module, details, ip_address, created_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        ev.get("user"),
                        ev.get("type", "event"),
                        "events",
                        json.dumps(ev, ensure_ascii=False),
                        ev.get("ip"),
                        ev.get("date", now_iso()),
                    ),
                )
            conn.commit()
        finally:
            conn.close()
