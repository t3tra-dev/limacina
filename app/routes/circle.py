from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Circle, CircleMember, User

circle_bp = Blueprint("circle", __name__)


@circle_bp.route("/", methods=["GET"])
def index():
    # サークル一覧表示(仮)
    circles = Circle.query.all()
    return render_template("circle/list.html", circles=circles)


@circle_bp.route("/<int:circle_id>", methods=["GET"])
def detail(circle_id):
    circle = Circle.query.get_or_404(circle_id)
    is_owner = circle.owner_id == current_user.id if current_user else False
    return render_template("circle/detail.html", circle=circle, is_owner=is_owner)


@circle_bp.route("/user_search", methods=["GET"])
@login_required
def user_search():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])

    # name または screen_name に部分一致
    results = (
        User.query.filter(
            (User.name.ilike(f"%{q}%")) | (User.screen_name.ilike(f"%{q}%"))
        )
        .limit(20)
        .all()
    )

    data = []
    for u in results:
        data.append({"id": u.id, "name": u.name, "screen_name": u.screen_name})

    return jsonify(data)


@circle_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        circle_name = request.form.get("circle_name", "").strip()
        circle_description = request.form.get("circle_description", "").strip()
        invite_user_ids_str = request.form.get(
            "invite_user_ids", ""
        )  # "1,2,3" のようなCSV想定

        errors = []
        if not circle_name:
            errors.append("サークル名は必須です。")

        # サークル名重複チェック
        if Circle.query.filter_by(name=circle_name).first():
            errors.append("このサークル名は既に使用されています。")

        # エラーがあればフォームに戻る
        if errors:
            return render_template(
                "circle/new_form.html",
                errors=errors,
                circle_name=circle_name,
                circle_description=circle_description,
            )

        # サークル作成
        new_circle = Circle(
            name=circle_name, description=circle_description, owner_id=current_user.id
        )
        db.session.add(new_circle)
        db.session.commit()

        # 自分自身をオーナーかつメンバーとして追加(approved)
        owner_member = CircleMember(
            user_id=current_user.id, circle_id=new_circle.id, status="approved"
        )
        db.session.add(owner_member)

        # 招待したいユーザーを pending で追加
        invite_user_ids = [
            uid.strip() for uid in invite_user_ids_str.split(",") if uid.strip()
        ]
        for uid in invite_user_ids:
            if uid.isdigit():
                uid_int = int(uid)
                # 重複や自分自身を改めて追加しないようにチェック
                if uid_int != current_user.id:
                    existing_member = CircleMember.query.filter_by(
                        user_id=uid_int, circle_id=new_circle.id
                    ).first()
                    if not existing_member:
                        cm = CircleMember(
                            user_id=uid_int, circle_id=new_circle.id, status="pending"
                        )
                        db.session.add(cm)

        db.session.commit()
        return redirect(url_for("circle.detail", circle_id=new_circle.id))

    return render_template("circle/new_form.html")


@circle_bp.route("/<int:circle_id>/edit", methods=["GET", "POST"])
@login_required
def edit_circle(circle_id):
    circle = Circle.query.get_or_404(circle_id)
    is_owner = circle.owner_id == current_user.id if current_user else False
    if not is_owner:
        abort(403, "このサークルを編集する権限がありません。")

    if request.method == "POST":
        # サークルの説明を更新
        circle_desc = request.form.get("circle_description", "")
        circle.description = circle_desc.strip()
        db.session.commit()

        # メンバーの削除処理
        remove_user_id_str = request.form.getlist("remove_user_id")
        for uid_str in remove_user_id_str:
            if uid_str.isdigit():
                cm = CircleMember.query.filter_by(circle_id=circle_id, user_id=int(uid_str)).first()
                # オーナーは自分自身を削除できないようにする
                if cm and cm.user_id != circle.owner_id:
                    db.session.delete(cm)
        db.session.commit()

        return redirect(url_for("circle.edit_circle", circle_id=circle_id))

    # メンバー一覧を取得(オーナーも含む)
    members = CircleMember.query.filter_by(circle_id=circle_id).all()
    return render_template("circle/edit.html", circle=circle, members=members, is_owner=is_owner)


@circle_bp.route("/<int:circle_id>/delete", methods=["POST"])
@login_required
def delete_circle(circle_id):
    circle = Circle.query.get_or_404(circle_id)
    if circle.owner_id != current_user.id:
        abort(403, "このサークルを削除する権限がありません。")

    # サークルに関連するメンバーも削除
    CircleMember.query.filter_by(circle_id=circle_id).delete()
    db.session.delete(circle)
    db.session.commit()

    # 削除後、サークル一覧ページなどにリダイレクト
    return redirect(url_for("circle.index"))
