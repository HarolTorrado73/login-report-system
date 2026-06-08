from app.services.alerts_service import create_alert


class AlertRouter:
    def route(self, payload):
        create_alert(payload)


alert_router = AlertRouter()
