import json

from flask import Blueprint, render_template

from app.services.report_service import (
    generate_report,
    generate_dashboard_stats,
    get_recent_activity     
)

main = Blueprint("main", __name__)


@main.route("/")
def home():

    with open("data/events.json", "r") as file:
        events = json.load(file)

    report = generate_report(events)

    stats = generate_dashboard_stats(report)

    recent_activity = get_recent_activity(events)

    return render_template(
    "index.html",
    report=report,
    stats=stats,
    recent_activity=recent_activity
)