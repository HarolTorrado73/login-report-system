import json
import os

from flask import Blueprint, render_template, request

from app.services.settings import get_settings, update_settings

settings = Blueprint("settings", __name__)


@settings.route("/settings", methods=["GET", "POST"])
def settings_page():
    if request.method == "POST":
        section = request.form.get("section")
        payload = {section: request.form.to_dict()}
        update_settings(payload)
    data = get_settings()
    return render_template("settings.html", settings=data)
