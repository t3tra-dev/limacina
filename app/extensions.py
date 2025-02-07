import json

from flask import Flask
from flask_login import LoginManager, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


def user_key_func():
    if current_user.is_authenticated:
        return str(current_user.id)
    return get_remote_address()


limiter = Limiter(
    key_func=user_key_func,
    default_limits=["200 per day", "50 per hour"],
)


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
