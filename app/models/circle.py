from datetime import UTC, datetime

from app.extensions import db


class Circle(db.Model):
    __tablename__ = "circles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    owner = db.relationship("User", back_populates="circle_owned")
    members = db.relationship(
        "CircleMember", back_populates="circle", cascade="all, delete-orphan"
    )

    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
        nullable=False,
    )


class CircleMember(db.Model):
    __tablename__ = "circle_members"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    circle_id = db.Column(db.Integer, db.ForeignKey("circles.id"), nullable=False)
    status = db.Column(
        db.String(16), default="pending", nullable=False
    )  # "pending", "approved"

    user = db.relationship("User", back_populates="circle_memberships")
    circle = db.relationship("Circle", back_populates="members")

    created_at = db.Column(db.DateTime, default=datetime.now(UTC), nullable=False)
