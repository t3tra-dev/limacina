import json

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def init_extensions(app: Flask):
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "ログインが必要です。"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def register_filters(app: Flask):
    @app.template_filter('json_loads')
    def json_loads_filter(s):
        try:
            return json.loads(s) if s else []
        except Exception:
            return []
