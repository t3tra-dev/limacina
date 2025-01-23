import datetime
import json
import os

import pytz
import requests
from flask import Blueprint, abort, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Event, Media, Post

__all__ = ["post_bp"]

post_bp = Blueprint("post", __name__)

api_token = os.environ["CLOUDFLARE_IMAGES_API_TOKEN"]
account_id = os.environ["CLOUDFLARE_ACCOUNT_ID"]
account_hash = os.environ["CLOUDFLARE_ACCOUNT_HASH"]

MEDIA_PROCESSORS = {
    "image": lambda source: f"https://imagedelivery.net/{account_hash}/{source}/public",
    "youtube": lambda source: f"https://www.youtube-nocookie.com/embed/{source}",
    "gist": lambda source: f"https://gist.github.com/{source}",
}


def upload_image_to_cloudflare(file) -> str:
    upload_url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1"

    response = requests.post(
        upload_url,
        headers={"Authorization": f"Bearer {api_token}"},
        files={"file": file},
    )

    if response.status_code != 200:
        raise RuntimeError("画像のアップロードに失敗しました")

    return response.json()["result"]["id"]


def delete_cloudflare_image(image_id: str) -> bool:
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/images/v1/{image_id}"
    response = requests.delete(url, headers={"Authorization": f"Bearer {api_token}"})
    return response.status_code == 200


def process_media(media: Media):
    processor = MEDIA_PROCESSORS.get(media.type)
    if processor:
        return {"type": media.type, "source": processor(media.source)}
    return {"type": media.type, "source": media.source}


def parse_tags(tag_string: str) -> list[str]:
    return [tag.strip() for tag in tag_string.split(",") if tag.strip()]


@post_bp.route("/<int:post_id>", methods=["GET"])
def detail(post_id):
    post = Post.query.get_or_404(post_id)
    is_own_post = current_user.is_authenticated and current_user.id == post.author_id

    now_utc = datetime.datetime.now(pytz.UTC)

    # 投稿の日時をUTCタイムゾーンに変換
    if post.start_date and not post.start_date.tzinfo:
        post.start_date = pytz.UTC.localize(post.start_date)
    if post.end_date and not post.end_date.tzinfo:
        post.end_date = pytz.UTC.localize(post.end_date)

    # 公開期間外チェック (投稿者じゃなければ閲覧不可)
    if not is_own_post:
        # 開始前
        if post.start_date and now_utc < post.start_date:
            abort(403, description="この投稿はまだ公開されていません。")
        # 終了後
        if post.end_date and now_utc > post.end_date:
            abort(403, description="この投稿の公開期間は終了しました。")

    processed_media = [process_media(media) for media in post.media]
    tags = json.loads(post.tags) if post.tags else []

    return render_template(
        "post/detail.html",
        post=post,
        processed_media=processed_media,
        is_own_post=is_own_post,
        tags=tags,
    )


@post_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        tags = request.form.get("tags", "").strip()
        files = request.files.getlist("media")
        embed_urls = request.form.get("embed_urls", "[]")

        start_date_str = request.form.get("start_date", "").strip()
        end_date_str = request.form.get("end_date", "").strip()

        event_id_str = request.form.get("event_id", "").strip()

        # タイトル必須
        if not title:
            abort(400, "タイトルは必須です。")

        # 日付をUTCに変換
        def parse_local_datetime(dt_str):
            if not dt_str:
                return None
            # 'YYYY-MM-DDTHH:MM' のようなdatetime-local形式をUTCに変換
            local_dt = datetime.datetime.fromisoformat(dt_str)  # ローカルタイムとして解釈
            # UTCへ変換
            return pytz.timezone("UTC").localize(local_dt)

        start_dt = parse_local_datetime(start_date_str)
        end_dt = parse_local_datetime(end_date_str)

        new_post = Post(
            title=title,
            description=description,
            tags=json.dumps(parse_tags(tags)),
            author_id=current_user.id,
            start_date=start_dt,
            end_date=end_dt,
        )

        if event_id_str.isdigit():
            new_post.event_id = int(event_id_str)
        else:
            new_post.event_id = None

        db.session.add(new_post)
        db.session.commit()

        # 画像メディアのアップロード
        for file in files:
            if file and file.filename:
                try:
                    image_id = upload_image_to_cloudflare(file)
                    if image_id:
                        media = Media(
                            type="image", source=image_id, post_id=new_post.id
                        )
                        db.session.add(media)
                except Exception:
                    continue

        # 埋め込みメディアの処理
        try:
            media_list = json.loads(embed_urls)
            for media_item in media_list:
                media_type = media_item.get("type")
                url = media_item.get("url")

                if media_type == "youtube":
                    video_id = extract_youtube_id(url)
                    if video_id:
                        media = Media(
                            type="youtube", source=video_id, post_id=new_post.id
                        )
                        db.session.add(media)
                elif media_type == "gist":
                    gist_id = extract_gist_id(url)
                    if gist_id:
                        media = Media(type="gist", source=gist_id, post_id=new_post.id)
                        db.session.add(media)
        except json.JSONDecodeError:
            raise Exception("埋め込みメディアのJSONパースエラー")
        except Exception as e:
            raise Exception(f"埋め込みメディア処理エラー: {str(e)}")

        db.session.commit()
        return redirect(url_for("post.detail", post_id=new_post.id))

    if request.method == "GET":
        events = Event.query.order_by(Event.start_date.asc()).all()
        return render_template("post/form.html", events=events)


@post_bp.route("/<int:post_id>/edit", methods=["GET", "POST"])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        abort(403)

    if request.method == "POST":
        post.title = request.form.get("title", post.title).strip()
        post.description = request.form.get("description", post.description).strip()
        tags = request.form.get("tags", "").strip()
        post.tags = json.dumps(parse_tags(tags))

        start_date_str = request.form.get("start_date", "").strip()
        end_date_str = request.form.get("end_date", "").strip()

        event_id_str = request.form.get("event_id", "").strip()

        def parse_local_datetime(dt_str):
            if not dt_str:
                return None
            local_dt = datetime.datetime.fromisoformat(dt_str)
            return pytz.timezone("UTC").localize(local_dt)

        post.start_date = parse_local_datetime(start_date_str)
        post.end_date = parse_local_datetime(end_date_str)

        if event_id_str.isdigit():
            post.event_id = int(event_id_str)
        else:
            post.event_id = None

        db.session.commit()
        return redirect(url_for("post.detail", post_id=post.id))

    if request.method == "GET":
        events = Event.query.order_by(Event.start_date.asc()).all()
        post_data = {
            "title": post.title,
            "description": post.description,
            "tags": json.loads(post.tags) if post.tags else [],
            "start_date": post.start_date,  # datetime or None
            "end_date": post.end_date,
        }
        return render_template("post/form.html", events=events, post=post_data)


@post_bp.route("/<int:post_id>/delete", methods=["POST"])
@login_required
def delete(post_id):
    """投稿の削除"""
    post = Post.query.get_or_404(post_id)
    if post.author_id != current_user.id:
        abort(403)

    # メディアの削除
    for media in post.media:
        if media.type == "image":
            delete_cloudflare_image(media.source)
        db.session.delete(media)

    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("main.index"))


def extract_youtube_id(url):
    import re

    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None


def extract_gist_id(url):
    import re

    match = re.search(r"gist\.github\.com\/([^\/]+\/[^\/]+)", url)
    return match.group(1) if match else None
