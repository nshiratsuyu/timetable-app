# ルーティング
# /blogs にHTTPメソッドがGETでアクセスしたblogs関数を実行する
from flask import Blueprint, render_template
# models.pyのBlogクラスをインポート
from flaskr.models import Blog

blog_bp = Blueprint("blog", __name__)

@blog_bp.route("/blogs")
def blogs():
    from flask import render_template
    # Blogテーブルから全てのデータを取得し、作成日時の降順で並び替え
    blogs = Blog.query.order_by(Blog.created_at.desc()).all()

    # テンプレートにblogs変数を渡す
    return render_template('blogs.html', blogs = blogs)