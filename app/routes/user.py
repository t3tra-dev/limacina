import os
import re

import requests
from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.user import User

__all__ = ["user_bp"]

user_bp = Blueprint("user", __name__)

api_token = os.environ["CLOUDFLARE_IMAGES_API_TOKEN"]
account_id = os.environ["CLOUDFLARE_ACCOUNT_ID"]
account_hash = os.environ["CLOUDFLARE_ACCOUNT_HASH"]


def is_valid_screen_name(screen_name: str) -> bool:
    return re.match(r"^[a-zA-Z0-9_-]+$", screen_name) is not None


def delete_cloudflare_image(image_id: str) -> bool:
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1/{image_id}"
    response = requests.delete(url, headers={"Authorization": f"Bearer {api_token}"})
    return response.status_code == 200


@user_bp.route("/@<screen_name>", methods=["GET"])
def profile(screen_name):
    user = User.query.filter_by(screen_name=screen_name).first()
    if not user:
        return render_template("errors/404.html"), 404

    approved_circles = [
        cm.circle for cm in user.circle_memberships if cm.status == "approved"
    ]

    # 投稿一覧 (最新順に並べるなら sorted / order_by など)
    user_posts = sorted(user.posts, key=lambda p: p.created_at, reverse=True)

    is_own_profile = current_user.is_authenticated and current_user.id == user.id
    return render_template(
        "user/profile.html",
        user=user,
        avatar_url=f"https://imagedelivery.net/{account_hash}/{user.avatar_id}/public",
        is_own_profile=is_own_profile,
        circles=approved_circles,
        posts=user_posts,
    )


@user_bp.route("/@<screen_name>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(screen_name):
    user = User.query.filter_by(screen_name=screen_name).first()
    if not user or user.id != current_user.id:
        return redirect(url_for("user.profile", screen_name=screen_name))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        bio = request.form.get("bio", "")
        avatar_file = request.files.get("avatar")
        remove_avatar = request.form.get("remove_avatar") == "true"

        if remove_avatar and user.avatar_id:
            delete_cloudflare_image(user.avatar_id)
            user.avatar_id = None

        if name:
            user.name = name

        user.bio = bio

        if avatar_file:
            if user.avatar_id:  # 既存アバターがあれば削除
                delete_cloudflare_image(user.avatar_id)

            upload_url = (
                f"https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1"
            )

            response = requests.post(
                upload_url,
                headers={"Authorization": f"Bearer {api_token}"},
                files={"file": avatar_file},
            )
            if response.status_code == 200:
                user.avatar_id = response.json()["result"]["id"]

        db.session.commit()
        return redirect(url_for("user.profile", screen_name=screen_name))

    return render_template(
        "user/edit_profile.html", user=user, account_hash=account_hash
    )
