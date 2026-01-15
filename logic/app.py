from flask import Flask, jsonify, request
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# =====================
# 初期設定
# =====================
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

BASE_DIR = os.path.dirname(__file__)
CLASSES_PATH = os.path.join(BASE_DIR, "classes.json")
FAVORITES_PATH = os.path.join(BASE_DIR, "favorites.json")
USERS_PATH = os.path.join(BASE_DIR, "users.json")
COMMENTS_PATH = os.path.join(BASE_DIR, "comments.json")
TIMETABLE_PATH = os.path.join(BASE_DIR, "timetable.json")

app = Flask(__name__)

# =====================
# AIコメント生成ロジック
# =====================
def generate_ai_comment(class_info):
    prompt = f"""
あなたは大学生向けの履修アドバイザーです。

次の授業を含む時間割について、
以下の観点のうち1点以上に触れて、
前向きなコメントを1〜3文で書いてください。
・忙しさのバランス
・重要な基礎科目である可能性
・時間割全体の一貫性

授業名: {class_info["name"]}
"""

    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt
    )

    return response.output_text or "とてもバランスの良い時間割ですね！"

# =====================
# 動作確認
# =====================
@app.route("/")
def index():
    return "API server running"

# =====================
# 授業検索API
# =====================
@app.route("/api/classes")
def get_classes():
    with open(CLASSES_PATH, encoding="utf-8") as f:
        classes = json.load(f)

    keyword = request.args.get("keyword")
    day = request.args.get("day")
    period = request.args.get("period")
    term = request.args.get("term")

    if keyword:
        classes = [c for c in classes if keyword in c["name"]]
    if day:
        classes = [c for c in classes if c["day"] == day]
    if period:
        classes = [c for c in classes if c["period"] == int(period)]
    if term:
        classes = [c for c in classes if c["term"] == int(term)]

    return jsonify({"classes": classes})

# =====================
# お気に入り取得（JOIN）
# =====================
@app.route("/api/favorites", methods=["GET"])
def get_favorites():
    user_id = int(request.args.get("user_id"))

    with open(FAVORITES_PATH, encoding="utf-8") as f:
        favorites = json.load(f)["favorites"]

    with open(CLASSES_PATH, encoding="utf-8") as f:
        classes = json.load(f)

    result = []
    for fav in favorites:
        if fav["user_id"] != user_id:
            continue

        class_data = next((c for c in classes if c["id"] == fav["class_id"]), None)
        if class_data:
            result.append({
                "favorite_id": fav["id"],
                "class": class_data
            })

    return jsonify({"favorites": result})

# =====================
# お気に入り追加
# =====================
@app.route("/api/favorites", methods=["POST"])
def add_favorite():
    body = request.get_json()
    user_id = body["user_id"]
    class_id = body["class_id"]

    with open(FAVORITES_PATH, encoding="utf-8") as f:
        data = json.load(f)

    for favo in data["favorites"]:
        if favo["user_id"] == user_id and favo["class_id"] == class_id:
            return jsonify({"error": "already favorited"}), 400

    new_id = len(data["favorites"]) + 1
    data["favorites"].append({
        "id": new_id,
        "user_id": user_id,
        "class_id": class_id
    })

    with open(FAVORITES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "ok"})

# =====================
# お気に入り削除API
# =====================
@app.route("/api/favorites/<int:favorite_id>", methods=["DELETE"])
def delete_favorite(favorite_id):
    with open(FAVORITES_PATH, encoding="utf-8") as f:
        data = json.load(f)

    before_count = len(data["favorites"])

    data["favorites"] = [
        fav for fav in data["favorites"]
        if fav["id"] != favorite_id
    ]

    if len(data["favorites"]) == before_count:
        return jsonify({
            "error": "favorite not found"
        }), 404

    with open(FAVORITES_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({
        "status": "deleted"
    })

# =====================
# コメントAPI
# =====================
@app.route("/api/comments", methods=["GET"])
def get_comments():
    class_id = int(request.args.get("class_id"))

    with open(COMMENTS_PATH, encoding="utf-8") as f:
        comments = json.load(f)["comments"]

    return jsonify({
        "comments": [c for c in comments if c["class_id"] == class_id]
    })

@app.route("/api/comments", methods=["POST"])
def add_comment():
    body = request.get_json()

    with open(COMMENTS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    new_id = len(data["comments"]) + 1
    data["comments"].append({
        "id": new_id,
        "user_id": body["user_id"],
        "class_id": body["class_id"],
        "content": body["content"]
    })

    with open(COMMENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({"status": "ok"})

# =====================
# コメント削除API
# =====================
@app.route("/api/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    with open(COMMENTS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    before_count = len(data["comments"])

    data["comments"] = [
        c for c in data["comments"]
        if c["id"] != comment_id
    ]

    # 見つからなかった場合
    if len(data["comments"]) == before_count:
        return jsonify({
            "error": "comment not found"
        }), 404

    with open(COMMENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({
        "status": "deleted"
    })

# =====================
# AIコメントAPI
# =====================
@app.route("/api/ai-comment")
def ai_comment():
    class_id = int(request.args.get("class_id"))

    with open(CLASSES_PATH, encoding="utf-8") as f:
        classes = json.load(f)

    class_info = next(c for c in classes if c["id"] == class_id)
    ai_text = generate_ai_comment(class_info)

    return jsonify({
        "success": True,
        "comment": ai_text
    })

# =====================
# 時間割登録API
# =====================
@app.route("/api/timetable", methods=["POST"])
def add_timetable():
    body = request.get_json()
    user_id = body["user_id"]
    class_id = body["class_id"]

    # 授業一覧を読む
    with open(CLASSES_PATH, encoding="utf-8") as f:
        classes = json.load(f)

    # 追加したい授業
    new_class = next(
    (c for c in classes if c["id"] == class_id),
    None
    )

    if not new_class:
        return jsonify({"error": "class not found"}), 404


    # 時間割を読む
    with open(TIMETABLE_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # ===== ① 二重登録チェック =====
    for t in data["timetables"]:
        if t["user_id"] == user_id and t["class_id"] == class_id:
            return jsonify({
                "error": "already registered"
            }), 400

    # ===== ② 時間かぶりチェック =====
    for t in data["timetables"]:
        if t["user_id"] != user_id:
            continue

        existing_class = next(
            (c for c in classes if c["id"] == t["class_id"]),
            None
        )

        if not existing_class:
            return jsonify({"error": "class not found"}), 404

        if (
            existing_class["day"] == new_class["day"]
            and existing_class["period"] == new_class["period"]
        ):
            return jsonify({
                "error": "time conflict",
                "conflict_with": {
                    "id": existing_class["id"],
                    "name": existing_class["name"],
                    "day": existing_class["day"],
                    "period": existing_class["period"]
                }
            }), 400

    # ===== ③ 登録処理 =====
    new_id = len(data["timetables"]) + 1
    timetable = {
        "id": new_id,
        "user_id": user_id,
        "class_id": class_id
    }

    data["timetables"].append(timetable)

    with open(TIMETABLE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({
        "status": "ok",
        "timetable": timetable
    })

# =====================
# 時間割取得API
# =====================
@app.route("/api/timetable", methods=["GET"])
def get_timetable():
    user_id = int(request.args.get("user_id"))

    with open(TIMETABLE_PATH, encoding="utf-8") as f:
        timetables = json.load(f)["timetables"]

    with open(CLASSES_PATH, encoding="utf-8") as f:
        classes = json.load(f)

    result = []

    for t in timetables:
        if t["user_id"] != user_id:
            continue

        class_data = next(
            (c for c in classes if c["id"] == t["class_id"]),
            None
        )

        if class_data:
            result.append({
                "class": class_data
            })

    return jsonify({ "timetable": result })

# =====================
# 時間割削除
# =====================
@app.route("/api/timetable/<int:timetable_id>", methods=["DELETE"])
def delete_timetable(timetable_id):
    with open(TIMETABLE_PATH, encoding="utf-8") as f:
        data = json.load(f)

    before_count = len(data["timetables"])

    data["timetables"] = [
        t for t in data["timetables"]
        if t["id"] != timetable_id
    ]

    # 見つからなかった場合
    if len(data["timetables"]) == before_count:
        return jsonify({
            "error": "timetable not found"
        }), 404

    with open(TIMETABLE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return jsonify({
        "status": "deleted"
    })

# =====================
# 起動
# =====================
if __name__ == "__main__":
    app.run(port=5002, debug=True)
