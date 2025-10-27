from flaskr import db
from datetime import datetime

class Blog(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    user_name = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def __repr__(self):
        return f'<Blog {self.title} by {self.user_name}>'

    def validate(self):
        """入力内容のバリデーションを行い、エラーを返す"""
        errors = []
        if not self.title or self.title.strip() == "":
            errors.append("タイトルを入力してください。")
        elif len(self.title) > 100:
            errors.append("タイトルは100文字以内で入力してください。")

        if not self.body or self.body.strip() == "":
            errors.append("本文を入力してください。")

        if not self.user_name or self.user_name.strip() == "":
            errors.append("投稿者名を入力してください。")
        elif len(self.user_name) > 50:
            errors.append("投稿者名は50文字以内で入力してください。")

        return errors