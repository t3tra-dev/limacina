from flask import Blueprint, render_template, request
from sqlalchemy import and_, or_

from app.models import Post

__all__ = ["main_bp"]

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("main/index.html")


@main_bp.route("/privacy")
def privacy():
    return render_template("main/privacy.html")


@main_bp.route("/terms")
def terms():
    return render_template("main/terms.html")


@main_bp.route("/search", methods=["GET"])
def search():
    query_text = request.args.get("q", "").strip()
    search_type = request.args.get("type", "text").strip()
    results = []

    if query_text:
        keywords = [kw.strip() for kw in query_text.split(",") if kw.strip()]

        # タイトル・本文検索
        if search_type == "text":
            results = Post.query.filter(
                and_(
                    *(or_(Post.title.ilike(f"%{kw}%"), Post.description.ilike(f"%{kw}%")) for kw in keywords)
                )
            ).order_by(Post.title.desc()).all()

        # タグ検索
        elif search_type == "tag":
            results = Post.query.filter(
                and_(*(Post.tags.ilike(f"%{kw}%") for kw in keywords))
            ).order_by(Post.title.desc()).all()

    return render_template("main/search.html", results=results, query=query_text, search_type=search_type)
