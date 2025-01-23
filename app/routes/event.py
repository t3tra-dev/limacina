from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

__all__ = ["event_bp"]

event_bp = Blueprint("event", __name__)


@event_bp.route("/", methods=["GET"])
def index():
    # イベント一覧表示
    events = []  # 後でデータベースから取得
    return render_template("event/list.html", events=events)


@event_bp.route("/<int:event_id>", methods=["GET"])
def detail(event_id):
    # イベント詳細表示
    event = {}  # 後でデータベースから取得
    return render_template("event/detail.html", event=event)


@event_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        # イベント作成処理（後で実装）
        flash("イベントが作成されました。", "success")
        return redirect(url_for("event.index"))
    return render_template("event/form.html")
