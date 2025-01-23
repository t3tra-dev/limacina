import os

from dotenv import load_dotenv
from flask import Flask, render_template

from app.extensions import db, init_extensions, register_filters
from app.routes import register_routes


def create_app():
    app = Flask("LIMACINA", template_folder="./app/templates")

    # アプリケーション設定
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///limacina.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

    # 拡張機能の初期化
    init_extensions(app)

    # ルートの登録
    register_routes(app)

    # フィルターの登録
    register_filters(app)

    # データベース初期化 (初回起動時)
    with app.app_context():
        db.create_all()

    @app.errorhandler(401)
    def unauthorized(e):
        return render_template("errors/401.html"), 401

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    return app


if __name__ == "__main__":
    load_dotenv(".env")
    app = create_app()
    app.run(host="0.0.0.0", port=3000, debug=True)
