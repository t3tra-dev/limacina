from datetime import UTC, datetime

from flask_login import UserMixin

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    screen_name = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    avatar_id = db.Column(db.String(256), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    roles = db.relationship(
        "UserRole", back_populates="user", cascade="all, delete-orphan"
    )
    posts = db.relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )
    comments = db.relationship(
        "Comment", back_populates="user", cascade="all, delete-orphan"
    )
    circle_owned = db.relationship(
        "Circle", back_populates="owner", cascade="all, delete-orphan"
    )
    circle_memberships = db.relationship(
        "CircleMember", back_populates="user", cascade="all, delete-orphan"
    )

    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
        nullable=False,
    )
