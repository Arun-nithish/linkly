from flask import Flask

from .db import init_db
from .routes import bp


def create_app(db_path: str = "linkly.db") -> Flask:
    """Application factory: lets tests create an app with a separate database."""
    app = Flask(__name__)
    app.config["DB_PATH"] = db_path
    init_db(db_path)
    app.register_blueprint(bp)
    return app
