# seed.py
# 初期データを投入するスクリプト
# flaskrパッケージのcreate_app関数とdbオブジェクトをインポート
from flaskr import create_app, db
# models.pyのBlogクラスをインポート
from flaskr.models import Blog

app = create_app()

with app.app_context():
    # 既存データを削除したい場合はコメントアウトを外す
    # db.drop_all()
    # db.create_all()

    blog1 = Blog(
        title="ごはん日記",
        body="お昼はカルボナーラ",
        user_name="yuki"
    )
    blog2 = Blog(
        title="好きな曲リスト",
        body="インフェルノ/ Mrs.Gただ君に晴れ/ヨルシカ",
        user_name="mai"
    )
    blog3 = Blog(
        title="気になる本",
        body="ファッション・パーツ図鑑",
        user_name="yuki"
    )

    db.session.add_all([blog1, blog2, blog3])
    db.session.commit()

    print("初期データを投入しました！")