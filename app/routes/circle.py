from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

__all__ = ["circle_bp"]

circle_bp = Blueprint("circle", __name__)


@circle_bp.route("/", methods=["GET"])
def index():
    # サークル一覧表示
    circles = []  # 後でデータベースから取得
    return render_template("circle/list.html", circles=circles)


@circle_bp.route("/<int:circle_id>", methods=["GET"])
def detail(circle_id):
    # サークル詳細表示
    circle = {}  # 後でデータベースから取得
    return render_template("circle/detail.html", circle=circle)


@circle_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        # サークル作成処理（後で実装）
        flash("サークルが作成されました。", "success")
        return redirect(url_for("circle.index"))
    return render_template("circle/form.html")


@circle_bp.route("/<int:circle_id>/members", methods=["POST"])
@login_required
def add_member(circle_id):
    # サークルメンバー追加処理（後で実装）
    flash("メンバー申請が送信されました。", "success")
    return redirect(url_for("circle.detail", circle_id=circle_id))
