from flask import Flask

from .admin import admin_bp
from .auth import auth_bp
from .circle import circle_bp
from .comment import comment_bp
from .event import event_bp
from .main import main_bp
from .notice import notice_bp
from .post import post_bp
from .user import user_bp

__all__ = ["register_routes"]


def register_routes(app: Flask):
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(circle_bp, url_prefix="/circles")
    app.register_blueprint(comment_bp, url_prefix="/comments")
    app.register_blueprint(event_bp, url_prefix="/events")
    app.register_blueprint(notice_bp, url_prefix="/notices")
    app.register_blueprint(post_bp, url_prefix="/posts")
    app.register_blueprint(user_bp, url_prefix="/users")

    app.register_blueprint(main_bp)
