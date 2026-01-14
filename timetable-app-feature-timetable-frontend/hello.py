# フレームワークに自分のアプリのためのプログラムを追加する
from flask import Flask, render_template

# テンプレートと静的ファイルの置き場所を定数に代入
TEMPLATE_PATH = 'templates'
STATIC_PATH = 'static'
# Flaskのインスタンスを作るときにそれを利用してファイルパスを設定する
app = Flask(__name__, template_folder=TEMPLATE_PATH, static_folder=STATIC_PATH)
# /（ルート）にアクセスしたら次に書く関数(hello_world)を実行するという宣言
@app.route("/")
def home():
    return render_template('home.html')