from flask import Flask
from models import db, User, Lesson

app = Flask(__name__)

# データベースの設定（SQLiteという簡単なファイル形式を使います）
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetable.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# データベースをアプリと連携
db.init_app(app)

# 動作確認用のテストルート
@app.route('/')
def hello():
    return "Backend is running!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 実行時にデータベースファイルを自動作成する
    app.run(debug=True)