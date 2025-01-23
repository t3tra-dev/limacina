from datetime import UTC, datetime

from app.extensions import db


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)

    users = db.relationship(
        "UserRole", back_populates="role", cascade="all, delete-orphan"
    )

    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)


class UserRole(db.Model):
    __tablename__ = "user_roles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)

    user = db.relationship("User", back_populates="roles")
    role = db.relationship("Role", back_populates="users")

    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)
