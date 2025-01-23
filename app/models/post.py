from datetime import datetime

from app.extensions import db


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tags = db.Column(db.Text, nullable=True)  # JSON文字列として保存
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    event = db.relationship("Event", back_populates="posts")
    author = db.relationship("User", back_populates="posts")
    media = db.relationship("Media", back_populates="post", cascade="all, delete-orphan")
    comments = db.relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    start_date = db.Column(db.DateTime, nullable=True)  # 公開開始日
    end_date = db.Column(db.DateTime, nullable=True)  # 公開終了日
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
