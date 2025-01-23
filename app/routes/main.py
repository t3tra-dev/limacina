from flask import Blueprint, render_template

__all__ = ["main_bp"]

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("main/index.html")
