import re

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.user import User

__all__ = ["auth_bp"]

auth_bp = Blueprint("auth", __name__)


def is_valid_screen_name(screen_name: str) -> bool:
    return re.match(r"^[a-zA-Z0-9_-]+$", screen_name) is not None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    errors = {}
    if request.method == "POST":
        screen_name = request.form.get("screen_name", "").strip()
        password = request.form.get("password", "").strip()

        if not screen_name:
            errors["screen_name"] = "ユーザーIDを入力してください。"
        if not password:
            errors["password"] = "パスワードを入力してください。"

        if not errors:
            user = User.query.filter_by(screen_name=screen_name).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for("main.index"))
            else:
                errors["general"] = "ユーザーIDまたはパスワードが間違っています。"

    return render_template("auth/login.html", errors=errors)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    errors = {}
    if request.method == "POST":
        screen_name = request.form.get("screen_name", "").strip()
        password = request.form.get("password", "").strip()

        if not screen_name:
            errors["screen_name"] = "ユーザーIDを入力してください。"
        elif not is_valid_screen_name(screen_name):
            errors["screen_name"] = (
                "ユーザーIDは半角英数字、ハイフン、アンダースコアのみ使用できます。"
            )
        elif User.query.filter_by(screen_name=screen_name).first():
            errors["screen_name"] = "このユーザーIDは既に使用されています。"
        if not password or len(password) < 8:
            errors["password"] = "パスワードは8文字以上で入力してください。"

        if not errors:
            hashed_password = generate_password_hash(password)
            new_user = User(
                name=screen_name, screen_name=screen_name, password=hashed_password
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("main.index"))

    return render_template("auth/register.html", errors=errors)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
