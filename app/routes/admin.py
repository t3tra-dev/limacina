from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

__all__ = ["admin_bp"]

admin_bp = Blueprint("admin", __name__)


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return func(*args, **kwargs)

    return wrapper


@admin_bp.route("/users", methods=["GET"])
@login_required
@admin_required
def users():
    # ユーザー一覧表示(後で実装)
    users = []  # 後でデータベースから取得
    return render_template("admin/users.html", users=users)


@admin_bp.route("/posts", methods=["GET"])
@login_required
@admin_required
def posts():
    # 投稿一覧表示(後で実装)
    posts = []  # 後でデータベースから取得
    return render_template("admin/posts.html", posts=posts)


@admin_bp.route("/posts/<int:post_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_post(post_id):
    # 投稿削除処理(後で実装)
    flash("投稿が削除されました。", "success")
    return redirect(url_for("admin.posts"))
