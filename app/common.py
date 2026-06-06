from flask import Blueprint, render_template

from app.services.report_service import (
    generate_sorted_report,
    generate_dashboard_stats,
    get_recent_activity,
    get_login_stats_by_day,
    get_session_distribution,
)


common = Blueprint("common", __name__)


@common.route("/dashboard")
def dashboard():
    events = []

    try:
        with open("data/events.json", "r", encoding="utf-8") as f:
            events = __import__("json", fromlist=["load"]).load(f)
    except Exception:
        events = []

    report = generate_sorted_report(events)
    stats = generate_dashboard_stats(report)
    recent_activity = get_recent_activity(events)
    login_stats = get_login_stats_by_day(events)
    session_distribution = get_session_distribution(report)

    return render_template(
        "dashboard.html",
        report=report,
        stats=stats,
        recent_activity=recent_activity,
        login_stats=login_stats,
        session_distribution=session_distribution,
    )
