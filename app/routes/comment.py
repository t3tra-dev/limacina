import datetime

from flask import Blueprint, redirect, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Comment, Post

__all__ = ["comment_bp"]

comment_bp = Blueprint("comment", __name__)


@comment_bp.route("/<int:post_id>/comments", methods=["POST"])
@login_required
def add_comment(post_id):
    """コメントまたは返信の投稿処理"""
    post = Post.query.get_or_404(post_id)

    content = request.form.get("content", "").strip()
    reply_to_id = request.form.get("reply_to_id", "").strip()  # 親コメントID(空ならroot)

    errors = {}
    if not content:
        errors["content"] = "コメント内容を入力してください。"

    if errors:
        return redirect(url_for("post.detail", post_id=post.id, **errors))

    # コメントを作成
    new_comment = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post.id,
        created_at=datetime.datetime.now(datetime.UTC)
    )
    # 親コメントがある場合
    if reply_to_id.isdigit():
        parent_comment = Comment.query.filter_by(id=int(reply_to_id), post_id=post.id).first()
        if parent_comment:
            new_comment.reply_to_id = parent_comment.id

    db.session.add(new_comment)
    db.session.commit()

    return redirect(url_for("post.detail", post_id=post.id, comment_success="true"))
