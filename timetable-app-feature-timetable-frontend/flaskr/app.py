import sys
import os
from flask import Flask, request, jsonify, session, render_template
from werkzeug.security import generate_password_hash, check_password_hash
# ▼▼▼ 追加：AIと環境変数のためのライブラリ ▼▼▼
from openai import OpenAI
from dotenv import load_dotenv

# インポート問題を解決
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# ↓↓↓ 最後に Timetable を追加しました ↓↓↓
from models import db, User, Lesson, Comment, Favorite, Timetable

# ▼▼▼ 追加：.envファイルを読み込む ▼▼▼
load_dotenv()

app = Flask(__name__)

# 設定
import os
# app.py があるフォルダの場所を特定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# データベースファイルをそのフォルダの中に作るように指定
db_path = os.path.join(BASE_DIR, 'timetable.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-123' 

db.init_app(app)

# ==================================================
#  [Helper] AIコメント生成ロジック (翻訳済み)
# ==================================================
def generate_ai_comment(lesson_title):
    # APIキーがない場合はダミーメッセージを返す（エラー防止）
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "（AI設定が未完了のため、自動生成コメントの代わりに表示しています）"

    prompt = f"""
    あなたは大学生向けの履修アドバイザーです。
    次の授業について、学生が興味を持つような前向きなコメントを1〜2文で書いてください。
    授業名: {lesson_title}
    """
    
    try:
        # クライアントを作成してリクエスト
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # コストが安いモデルを指定
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"AI Error: {e}")
        return "AIコメントの生成に失敗しました。"

# ==================================================
#  0. 画面表示用ルート
# ==================================================

# 1. ホーム画面（index.html）
@app.route('/')
def home():
    return render_template('index.html')

# 2. 時間割画面（timetable.html）
@app.route('/timetable')
def timetable():
    # 本来はログイン中のユーザーIDを使いますが、今はテスト用に ID=1 と仮定します
    current_user_id = 1 
    
    # Timetableテーブルから、自分の登録データを探す
    my_entries = Timetable.query.filter_by(user_id=current_user_id).all()
    
    # 登録データから「授業の詳細情報」を取り出す
    my_lessons = []
    for entry in my_entries:
        lesson = Lesson.query.get(entry.lesson_id)
        if lesson:
            my_lessons.append(lesson)

    return render_template('timetable.html', lessons=my_lessons)

# 3. お気に入り画面（favorites.html）
@app.route('/favorites')
def favorites():
    my_favorites = Favorite.query.all() 
    return render_template('favorites.html', favorites=my_favorites)

# 4. コメント画面（comments.html）
@app.route('/comments')
def comments():
    all_comments = Comment.query.all()
    return render_template('comments.html', comments=all_comments)

# 5. 授業検索画面（search.html）
@app.route('/search')
def search_classes():
    return render_template('search.html')

# ==================================================
#  1. ユーザー管理 API
# ==================================================
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data['username']).first():
        return jsonify({"message": "このユーザー名は既に使われています"}), 400
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
        session['user_id'] = user.id
        return jsonify({"message": f"ログイン成功。ようこそ {user.username}さん"}), 200
    return jsonify({"message": "名前またはパスワードが違います"}), 401

# ==================================================
#  2. 授業データ API (基本CRUD)
# ==================================================
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
    
    lessons = Lesson.query.all()
    return jsonify([{
        "id": l.id, "title": l.title, "teacher": l.teacher,
        "day": l.day_of_week, "period": l.period
    } for l in lessons])

# ==================================================
#  3. [移植・翻訳] 授業検索 API
# ==================================================
@app.route("/api/classes")
def get_classes():
    # URLパラメータを取得 (?keyword=数学&day=月...)
    keyword = request.args.get("keyword")
    day = request.args.get("day")
    period = request.args.get("period")

    # 検索の準備（まずは全件）
    query = Lesson.query

    # 条件があれば絞り込み (SQLの WHERE に相当)
    if keyword:
        query = query.filter(Lesson.title.contains(keyword))
    if day:
        query = query.filter(Lesson.day_of_week == day)
    if period:
        query = query.filter(Lesson.period == int(period))

    # 検索実行
    lessons = query.all()

    # JSON形式にして返す
    return jsonify({
        "classes": [{
            "id": l.id,
            "name": l.title,      # フロント側の "name" に合わせる
            "teacher": l.teacher,
            "day": l.day_of_week,
            "period": l.period
        } for l in lessons]
    })

# ==================================================
#  4. [移植・翻訳] AIコメント API
# ==================================================
@app.route("/api/ai-comment")
def ai_comment():
    # URLパラメータから授業IDを取得
    lesson_id = request.args.get("class_id")
    
    if not lesson_id:
        return jsonify({"success": False, "message": "授業IDが必要です"})

    # データベースから授業を探す
    lesson = Lesson.query.get(lesson_id)
    
    if not lesson:
        return jsonify({"success": False, "message": "授業が見つかりません"})

    # 上で作ったAI関数を呼び出す
    ai_text = generate_ai_comment(lesson.title)

    return jsonify({
        "success": True,
        "comment": ai_text
    })

# ==================================================
#  起動設定
# ==================================================

# テーブル作成コマンド（flask runでも実行されるように外に出しました）
with app.app_context():
    db.create_all()

# 時間割に授業を登録するAPI
@app.route('/api/timetable', methods=['POST'])
def add_to_timetable():
    data = request.get_json()
    user_id = 1  # テスト用ユーザーID
    lesson_id = data.get('class_id')

    # 重複チェック（既に登録済みなら何もしない）
    existing = Timetable.query.filter_by(user_id=user_id, lesson_id=lesson_id).first()
    if existing:
        return jsonify({"message": "この授業は既に登録されています"}), 400

    # 登録
    new_entry = Timetable(user_id=user_id, lesson_id=lesson_id)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({"message": "時間割に追加しました！"}), 201

if __name__ == '__main__':
    app.run(debug=True)