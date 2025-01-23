from app.extensions import db


class Media(db.Model):
    __tablename__ = "media"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(16), nullable=False)  # "image" または "embed"
    source = db.Column(db.String, nullable=False)  # IDまたはURLを保存
    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"), nullable=False)

    post = db.relationship("Post", back_populates="media")
