import json
from app import app, db
from models import Lesson

def import_classes():
    print("🚀 データのインポートを開始します...")

    # 1. JSONファイルを読み込む
    try:
        with open('classes.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # dataがリストか、辞書の中のリストかを確認
            if isinstance(data, dict) and 'classes' in data:
                classes_list = data['classes']
            elif isinstance(data, list):
                classes_list = data
            else:
                print("❌ JSONの形式が予想と違いました")
                return
    except FileNotFoundError:
        print("❌ 'classes.json' が見つかりません。flaskrフォルダに置きましたか？")
        return

    # 2. データベースに登録する
    with app.app_context():
        # 重複を防ぐため、一旦中身をリセットしたい場合は下の行のコメント(#)を外す
        # db.session.query(Lesson).delete()
        
        count = 0
        for item in classes_list:
            # JSONの項目名(name)を、DBの項目名(title)に合わせる
            # ※ teacherがない場合は "未定" にする
            new_lesson = Lesson(
                title=item.get('name'),         # JSONの 'name'
                teacher=item.get('teacher', '担当教員未定'), # teacherがない場合
                day_of_week=item.get('day'),    # JSONの 'day'
                period=item.get('period')       # JSONの 'period'
            )
            db.session.add(new_lesson)
            count += 1
        
        db.session.commit()
        print(f"✅ {count} 件の授業データをデータベースに登録しました！")

if __name__ == '__main__':
    import_classes()