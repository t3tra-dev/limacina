from datetime import datetime

from app.extensions import db


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)
    reply_to_id = db.Column(db.Integer, db.ForeignKey("comments.id"), nullable=True)

    user = db.relationship("User", back_populates="comments")
    post = db.relationship("Post", back_populates="comments")
    replies = db.relationship(
        "Comment",
        backref=db.backref("reply_to", remote_side=[id]),
        cascade="all, delete-orphan",
        single_parent=True,
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
