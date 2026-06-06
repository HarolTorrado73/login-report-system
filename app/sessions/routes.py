from flask import Blueprint, render_template, request, jsonify, redirect, url_for

from app.services.sessions import get_sessions, terminate_session

sessions = Blueprint("sessions", __name__)


@sessions.route("/sessions")
def sessions_page():
    all_sessions = get_sessions()
    active = [s for s in all_sessions if s["active"]]
    finished = [s for s in all_sessions if not s["active"]]
    status = request.args.get("status", "all")
    if status == "active":
        view = active
    elif status == "finished":
        view = finished
    else:
        view = all_sessions
    return render_template(
        "sessions.html",
        sessions=view,
        active_count=len(active),
        finished_count=len(finished),
        status=status,
    )


@sessions.route("/sessions/terminate", methods=["POST"])
def terminate():
    user = request.form.get("user")
    machine = request.form.get("machine")
    if not user or not machine:
        return jsonify({"ok": False, "error": "Datos incompletos"}), 400
    ok = terminate_session(user, machine)
    return jsonify({"ok": ok})
