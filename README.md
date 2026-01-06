# timetable-app

## ロジック
## 現在できていること
- 仮の大学学部学科学年を想定した授業一覧データをCSV → JSONに変換
- FlaskでAPIサーバーを起動
- 授業一覧取得APIを実装
- 授業検索API（keyword）、ログインAPI、お気に入りAPI、時間割登録を実装
## API一覧
## 授業一覧取得API http://localhost:5002/api/classes
GET /api/classes
### 授業検索で絞り込み
GET /api/classes?keyword=&day=&period=&term=
## ログインAPI（簡易実装）※ 現在はダミー実装。
POST /api/login
### リクエスト
{
  "username": "testuser",
  "password": "password"
}
### レスポンス
{
  "status": "ok",
  "user_id": 1
}
## お気に入りAPI(授業一覧から、ユーザーがお気に入り登録した授業を管理するAPI)
### お気に入り一覧取得（授業情報付き）
- **URL**: `/api/favorites`
- **Method**: `GET`
- **Description**:  
  お気に入り登録された授業を、授業情報（授業名・曜日・時限など）と一緒に取得します。
#### Response Example
```json
{
  "favorites": [
    {
      "favorite_id": 1,
      "class": {
        "id": 3,
        "term": 1,
        "day": "月",
        "period": 3,
        "name": "English I",
        "location": "B101"
      }
    }
  ]
}

### 時間割登録API
POST /api/timetable
### リクエスト
{
  "user_id": 1,
  "class_id": 3
}
### レスポンス
{
  "status": "ok",
  "timetable": {
    "id": 1,
    "user_id": 1,
    "class_id": 3
  }
}

### 時間割取得API
GET /api/timetable?user_id=1
### レスポンス
{
  "timetable": [
    {
      "class": {
        "id": 3,
        "name": "...",
        "day": "Mon",
        "period": 2
      }
    }
  ]
}