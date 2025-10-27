from flask import Flask
# SQLAlchemyをインポート
from flask_sqlalchemy import SQLAlchemy
# SQLAlchemyのdeclarative_baseをインポート
from sqlalchemy.orm import declarative_base

Base = declarative_base()
db = SQLAlchemy()  # ここでインスタンス作成

def create_app():
    # アプリケーションのインスタンスを作成
    app = Flask(__name__)
    # 🔑 セッション・flash()・ログイン用に必須
    app.config['SECRET_KEY'] = 'dev'  # 開発用（本番では安全なランダム文字列に変更）

    # SQLiteのデータベースファイルを指定
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskr.db'
    # SQLAlchemyの設定を無効化
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)  # SQLAlchemyのインスタンスをアプリに紐付け

    # blueprintの登録
    from . import blogs
    app.register_blueprint(blogs.blog_bp)

    # データベースのテーブルを作成
    with app.app_context():
        db.create_all()

    return app