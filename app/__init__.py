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

    app.register_blueprint(auth)
    app.register_blueprint(common)

    return app