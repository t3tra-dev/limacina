import datetime
from functools import wraps

import pytz
from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db, limiter
from app.models import Event

__all__ = ["event_bp"]

event_bp = Blueprint("event", __name__)


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return func(*args, **kwargs)

    return wrapper


@event_bp.route("/", methods=["GET"])
@limiter.limit("30 per minute")
def index():
    events = Event.query.order_by(Event.start_date.asc()).all()
    return render_template("event/list.html", events=events)


@event_bp.route("/<int:event_id>", methods=["GET"])
def detail(event_id):
    event = Event.query.get_or_404(event_id)
    return render_template("event/detail.html", event=event)


@event_bp.route("/new", methods=["GET", "POST"])
@login_required
@admin_required
def new():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        start_date_str = request.form.get("start_date", "").strip()
        end_date_str = request.form.get("end_date", "").strip()

        # バリデーション(タイトル必須・日付必須など)
        if not title or not start_date_str or not end_date_str:
            abort(400, description="タイトル, 開始日, 終了日は必須です。")

        # 日付をUTCに変換
        def parse_local_datetime(dt_str):
            local_dt = datetime.datetime.fromisoformat(dt_str)  # 'YYYY-MM-DDTHH:MM'
            return pytz.timezone("UTC").localize(local_dt)

        start_dt = parse_local_datetime(start_date_str)
        end_dt = parse_local_datetime(end_date_str)

        if start_dt >= end_dt:
            abort(400, description="開始日は終了日より前に設定してください。")

        # イベント作成
        new_event = Event(
            title=title,
            description=description,
            start_date=start_dt,
            end_date=end_dt,
        )
        db.session.add(new_event)
        db.session.commit()

        return redirect(url_for("event.index"))

    return render_template("event/new_form.html")


@event_bp.route("/<int:event_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for("event.index"))
