from collections import defaultdict, OrderedDict
from datetime import datetime


def get_event_date(event):
    return event["date"]


def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return None


def generate_report(events):
    machines = {}

    for event in events:
        machine = event["machine"]
        user = event["user"]
        event_type = event["type"]

        if machine not in machines:
            machines[machine] = set()

        if event_type == "login":
            machines[machine].add(user)

        elif event_type == "logout":
            machines[machine].discard(user)

    return machines


def generate_dashboard_stats(report):
    total_machines = len(report)
    active_users = set()

    for users in report.values():
        active_users.update(users)

    total_active_users = len(active_users)

    total_sessions = sum(
        len(users) for users in report.values()
    )

    return {
        "total_machines": total_machines,
        "total_active_users": total_active_users,
        "total_sessions": total_sessions,
    }


def get_recent_activity(events):
    ordered_events = sorted(
        events,
        key=get_event_date,
        reverse=True,
    )

    return ordered_events[:5]


def sort_events(events):
    return sorted(events, key=get_event_date)


def generate_sorted_report(events):
    events = sort_events(list(events))
    machines = {}

    for event in events:
        machine = event["machine"]
        user = event["user"]
        event_type = event["type"]

        if machine not in machines:
            machines[machine] = set()

        if event_type == "login":
            machines[machine].add(user)

        elif event_type == "logout":
            machines[machine].discard(user)

    return machines


def get_login_stats_by_day(events):
    stats = defaultdict(int)

    for event in events:
        if event.get("type") != "login":
            continue

        parsed = parse_date(event.get("date", ""))
        if not parsed:
            continue

        day = parsed.strftime("%Y-%m-%d")
        stats[day] += 1

    sorted_stats = OrderedDict(sorted(stats.items()))
    labels = list(sorted_stats.keys())
    values = list(sorted_stats.values())

    return {"labels": labels, "values": values}


def get_session_distribution(report):
    active = sum(1 for users in report.values() if users)
    inactive = sum(1 for users in report.values() if not users)

    return {
        "labels": ["Active", "Inactive"],
        "values": [active, inactive],
    }


def get_user_activity_stats(users_path):
    try:
        with open(users_path, "r", encoding="utf-8") as f:
            users = json.load(f)
    except (OSError, json.JSONDecodeError):
        users = []

    total_users = len(users)
    active_users = sum(1 for user in users if user.get("status") == "active")
    admins = sum(1 for user in users if user.get("role") == "admin")
    analysts = sum(1 for user in users if user.get("role") == "analyst")
    viewers = sum(1 for user in users if user.get("role") == "viewer")

    return {
        "total_users": total_users,
        "active_users": active_users,
        "admins": admins,
        "analysts": analysts,
        "viewers": viewers,
    }