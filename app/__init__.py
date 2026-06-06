import os

from dotenv import load_dotenv

from flask import Flask

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    from app.auth import auth
    from app.common import common
    from app.machines.routes import machines
    from app.sessions.routes import sessions
    from app.reports.routes import reports
    from app.settings.routes import settings as settings_bp

    app.register_blueprint(auth)
    app.register_blueprint(common)
    app.register_blueprint(machines)
    app.register_blueprint(sessions)
    app.register_blueprint(reports)
    app.register_blueprint(settings_bp)

    return app