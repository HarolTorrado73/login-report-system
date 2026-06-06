import json
import os

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

from app.services.report_service import (
    generate_sorted_report,
    generate_dashboard_stats,
    get_recent_activity,
    get_login_stats_by_day,
    get_session_distribution,
)

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Debe ingresar usuario y contrasena.", "error")
            return render_template("login.html")

        users_data = load_users()
        user = next((u for u in users_data if u["username"] == username), None)

        if not user or not user.get("password_hash"):
            flash("Credenciales invalidas.", "error")
            return render_template("login.html")

        if not check_password_hash(user["password_hash"], password):
            flash("Credenciales invalidas.", "error")
            return render_template("login.html")

        if user.get("status") != "active":
            flash("Usuario inactivo. Contacte al administrador.", "error")
            return render_template("login.html")

        session.clear()
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]
        session.permanent = True

        return redirect(url_for("auth.dashboard"))

    return render_template("login.html")


@auth.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        flash("Inicie sesion para acceder al dashboard.", "error")
        return redirect(url_for("auth.login"))

    try:
        events = load_events()
    except Exception:
        events = []

    report = generate_sorted_report(events)
    stats = generate_dashboard_stats(report)
    recent = get_recent_activity(events)
    login_stats = get_login_stats_by_day(events)
    session_dist = get_session_distribution(report)

    return render_template(
        "dashboard.html",
        user=session.get("username", ""),
        role=session.get("role", "viewer"),
        report=report,
        stats=stats,
        recent_activity=recent,
        login_stats=login_stats,
        session_distribution=session_dist,
    )


@auth.route("/logout")
def logout():
    session.clear()
    flash("Sesion cerrada correctamente.", "success")
    return redirect(url_for("auth.login"))


@auth.route("/api/events", methods=["POST"])
def api_add_event():
    raw_event = request.get_json(silent=True)
    if not raw_event:
        return {"ok": False, "errors": ["JSON invalido o vacio"]}, 400

    return {"ok": True, "event": raw_event}


def load_events():
    with open("data/events.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_users():
    users_path = users_json_path()
    with open(users_path, "r", encoding="utf-8") as f:
        return json.load(f)


def users_json_path():
    return os.path.join(os.path.dirname(__file__), "..", "data", "users.json")
