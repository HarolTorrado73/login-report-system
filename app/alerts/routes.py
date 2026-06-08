from flask import Blueprint, render_template

from app.services.alert_router import alert_router
from app.services.alerts_service import (
    get_alerts,
    get_alert,
    create_alert,
    update_alert,
    resolve_alert,
)

alerts = Blueprint("alerts", __name__)


@alerts.route("/alerts")
def alerts_page():
    items = get_alerts()
    return render_template("alerts.html", items=items)


@alerts.route("/alerts/<int:alert_id>")
def alert_detail(alert_id: int):
    item = get_alert(alert_id)
    return render_template("alert_detail.html", item=item or {})


@alerts.route("/alerts", methods=["POST"])
def alerts_create():
    payload = {
        "title": __import__("flask").request.form.get("title", ""),
        "description": __import__("flask").request.form.get("description", ""),
        "severity": __import__("flask").request.form.get("severity", "medium"),
        "status": __import__("flask").request.form.get("status", "open"),
    }
    alert_router.route({
        "action": "create",
        "payload": payload,
        "source": "web_ui",
    })
    create_alert(payload)
    return __import__("flask").redirect(__import__("flask").url_for("alerts.alerts_page"))


@alerts.route("/alerts/<int:alert_id>", methods=["POST"])
def alerts_update(alert_id: int):
    payload = {
        "title": __import__("flask").request.form.get("title", ""),
        "description": __import__("flask").request.form.get("description", ""),
        "severity": __import__("flask").request.form.get("severity", "medium"),
        "status": __import__("flask").request.form.get("status", "open"),
    }
    update_alert(alert_id, payload)
    return __import__("flask").redirect(__import__("flask").url_for("alerts.alerts_page"))


@alerts.route("/alerts/<int:alert_id>/resolve", methods=["POST"])
def alerts_resolve(alert_id: int):
    resolve_alert(alert_id)
    return __import__("flask").redirect(__import__("flask").url_for("alerts.alerts_page"))
