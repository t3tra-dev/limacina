from flask import Blueprint, flash, redirect, request, url_for
from flask_login import login_required

__all__ = ["comment_bp"]

comment_bp = Blueprint("comment", __name__)


@comment_bp.route("/<int:post_id>/comments", methods=["POST"])
@login_required
def add_comment(post_id):
    # コメント作成処理(後で実装)
    flash("コメントが追加されました。", "success")
    return redirect(url_for("post.detail", post_id=post_id))


@comment_bp.route("/<int:comment_id>/reply", methods=["POST"])
@login_required
def reply(comment_id):
    # コメントへの返信処理(後で実装)
    flash("返信が追加されました。", "success")
    return redirect(request.referrer or "/")
