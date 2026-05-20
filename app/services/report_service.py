def get_event_date(event):
    return event["date"]


def generate_report(events):
    events.sort(key=get_event_date)

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