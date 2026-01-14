from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Lesson, Comment, Favorite

app = Flask(__name__)

# 設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///timetable.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-123' # セッション管理に必要

db.init_app(app)

# ---------------------------------------
# 1. ユーザー管理（登録・ログイン）
# ---------------------------------------

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "このユーザー名は既に使われています"}), 400
    
    # パスワードを暗号化して保存
    hashed_pw = generate_password_hash(data['password'])
    new_user = User(username=data['username'], password=hashed_pw)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "登録完了"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password, data['password']):
        session['user_id'] = user.id # ログイン状態を保存
        return jsonify({"message": f"ログイン成功。ようこそ {user.username}さん"}), 200
    return jsonify({"message": "名前またはパスワードが違います"}), 401

@app.route('/api/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "ログアウトしました"})

# ---------------------------------------
# 2. 授業データの管理
# ---------------------------------------

@app.route('/api/lessons', methods=['GET', 'POST'])
def handle_lessons():
    if request.method == 'POST':
        data = request.get_json()
        new_lesson = Lesson(
            title=data['title'],
            teacher=data.get('teacher'),
            day_of_week=data['day_of_week'],
            period=data['period']
        )
        db.session.add(new_lesson)
        db.session.commit()
        return jsonify({"message": "授業を追加しました"}), 201
    
    # 一覧取得
    lessons = Lesson.query.all()
    return jsonify([{
        "id": l.id, "title": l.title, "teacher": l.teacher,
        "day": l.day_of_week, "period": l.period
    } for l in lessons])

# ---------------------------------------
# 3. コメント保存
# ---------------------------------------

@app.route('/api/lessons/<int:lesson_id>/comment', methods=['POST'])
def add_comment(lesson_id):
    if 'user_id' not in session:
        return jsonify({"message": "ログインが必要です"}), 401
    
    data = request.get_json()
    new_comment = Comment(
        content=data['content'],
        user_id=session['user_id'],
        lesson_id=lesson_id
    )
    db.session.add(new_comment)
    db.session.commit()
    return jsonify({"message": "コメントを保存しました"}), 201

# ---------------------------------------
# 4. お気に入り保存
# ---------------------------------------

@app.route('/api/lessons/<int:lesson_id>/favorite', methods=['POST'])
def toggle_favorite(lesson_id):
    if 'user_id' not in session:
        return jsonify({"message": "ログインが必要です"}), 401
    
    uid = session['user_id']
    fav = Favorite.query.filter_by(user_id=uid, lesson_id=lesson_id).first()
    
    if fav:
        db.session.delete(fav) # 既にあれば解除
        msg = "お気に入りを解除しました"
    else:
        new_fav = Favorite(user_id=uid, lesson_id=lesson_id)
        db.session.add(new_fav) # なければ登録
        msg = "お気に入りに追加しました"
    
    db.session.commit()
    return jsonify({"message": msg})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
@app.route('/')
def index():
    return "Backend API is running! Try /api/lessons"
    app.run(debug=True)