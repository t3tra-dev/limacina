from flask import Blueprint, render_template
from flask_login import login_required, current_user

from app.models import CircleMember, Comment, Post

notice_bp = Blueprint("notice", __name__)


@notice_bp.route("/", methods=["GET"])
@login_required
def notices():
    user_id = current_user.id

    invites = (
        CircleMember.query
        .filter_by(user_id=user_id, status="pending")
        .order_by(CircleMember.created_at.desc())
        .all()
    )

    invite_notices = []
    for inv in invites:
        invite_notices.append({
            "type": "circle_invite",
            "created_at": inv.created_at,
            "circle_id": inv.circle_id,
            "circle_name": inv.circle.name,
            "message": f"「{inv.circle.name}」への招待が届いています",
        })

    my_post_comments = (
        Comment.query
        .join(Post, Comment.post_id == Post.id)
        .filter(Post.author_id == user_id, Comment.user_id != user_id)
        .order_by(Comment.created_at.desc())
        .all()
    )
    comment_notices = []
    for c in my_post_comments:
        comment_notices.append({
            "type": "comment_on_my_post",
            "created_at": c.created_at,
            "post_id": c.post_id,
            "post_title": c.post.title,
            "comment_id": c.id,
            "comment_user": c.user.screen_name,
            "message": "あなたの投稿にコメントがありました",
        })

    my_comment_replies = (
        Comment.query
        .filter(Comment.reply_to_id.isnot(None))
        .filter(Comment.reply_to.has(user_id=user_id))
        .filter(Comment.user_id != user_id)
        .order_by(Comment.created_at.desc())
        .all()
    )
    reply_notices = []
    for c in my_comment_replies:
        for c in my_comment_replies:
            reply_notices.append({
                "type": "reply_to_my_comment",
                "created_at": c.created_at,
                "post_id": c.post_id,
                "post_title": c.post.title,
                "comment_id": c.id,
                "comment_user": c.user.screen_name,
                "comment_user_name": c.user.name,
                "message": f"「{c.post.title}」についてのあなたのコメントへの返信があります",
            })

    notices_list = invite_notices + comment_notices + reply_notices
    notices_list.sort(key=lambda x: x["created_at"], reverse=True)

    return render_template("notice/list.html", notices=notices_list)
