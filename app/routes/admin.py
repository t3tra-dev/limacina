from functools import wraps
from flask import Blueprint, abort
from flask_login import current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView

from app.extensions import db
from app.models import (
    User,
    Post,
    Comment,
    Circle,
    CircleMember,
    Event,
    Media,
    Role,
    UserRole,
)

__all__ = ["admin_bp"]

admin_bp = Blueprint("admin", __name__)


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return func(*args, **kwargs)

    return wrapper


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        abort(403)


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        abort(403)


def init_admin(app):
    admin = Admin(
        app,
        name="Limacina Admin",
        template_mode="bootstrap4",
        index_view=MyAdminIndexView(url="/admin"),
    )

    # Users
    admin.add_view(
        AdminModelView(
            User, db.session, endpoint="admin_user", url="/admin/user", category="Users"
        )
    )
    admin.add_view(
        AdminModelView(
            Role, db.session, endpoint="admin_role", url="/admin/role", category="Users"
        )
    )
    admin.add_view(
        AdminModelView(
            UserRole,
            db.session,
            endpoint="admin_user_role",
            url="/admin/user-role",
            category="Users",
        )
    )

    # Posts
    admin.add_view(
        AdminModelView(
            Post, db.session, endpoint="admin_post", url="/admin/post", category="Posts"
        )
    )
    admin.add_view(
        AdminModelView(
            Comment,
            db.session,
            endpoint="admin_comment",
            url="/admin/comment",
            category="Posts",
        )
    )
    admin.add_view(
        AdminModelView(
            Media,
            db.session,
            endpoint="admin_media",
            url="/admin/media",
            category="Posts",
        )
    )

    # Circles
    admin.add_view(
        AdminModelView(
            Circle,
            db.session,
            endpoint="admin_circle",
            url="/admin/circle",
            category="Circles",
        )
    )
    admin.add_view(
        AdminModelView(
            CircleMember,
            db.session,
            endpoint="admin_circle_member",
            url="/admin/circle-member",
            category="Circles",
        )
    )

    # Events
    admin.add_view(
        AdminModelView(
            Event,
            db.session,
            endpoint="admin_event",
            url="/admin/event",
            category="Events",
        )
    )

    return admin
