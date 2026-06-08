#!/usr/bin/env python3
"""Entrypoint with DB init."""

from app import create_app
from app.services.db import init_db as init_sqlite

app = create_app()

with app.app_context():
    init_sqlite(seed=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
