events = [
    {"date": "2026-05-20 08:00", "user": "ana", "machine": "PC-01", "type": "login"},
    {"date": "2026-05-20 08:10", "user": "carlos", "machine": "PC-01", "type": "login"},
    {"date": "2026-05-20 08:30", "user": "ana", "machine": "PC-01", "type": "logout"},
    {"date": "2026-05-20 09:00", "user": "maria", "machine": "PC-02", "type": "login"},
]


def get_event_date(event):
    return event["date"]


def generate_report(events_list):
    events_list.sort(key=get_event_date)

    machines = {}

    for event in events_list:
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