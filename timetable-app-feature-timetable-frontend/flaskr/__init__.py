from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flaskr.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from . import blogs
    app.register_blueprint(blogs.blog_bp)

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/timetable')
    def timetable():
        return render_template('timetable.html')

    @app.route('/favorites')
    def favorites():
        return "お気に入り授業ページ（仮）"

    @app.route('/comments')
    def comments():
        return "コメントページ（仮）"

    @app.route('/search_classes')
    def search_classes():
        return "授業検索ページ（仮）"

    with app.app_context():
        db.create_all()

    return app
