from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskr.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Blueprint の登録
    from . import blogs
    app.register_blueprint(blogs.blog_bp)

    # ★ タイムテーブル画面のルート（ここが重要）
    @app.route('/timetable')
    def timetable():
        return render_template('timetable.html')

    # DB テーブル作成
    with app.app_context():
        db.create_all()

    return app
