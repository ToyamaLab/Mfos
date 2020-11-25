from sqlalchemy import func, CheckConstraint
from flaskr.database import db


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True)  # 主キー
    name = db.Column(db.String(20), index=True, nullable=False)  # デフォルト値
    slack_id = db.Column(db.String(20), index=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)

    def __init__(self, name, slack_id, created_at, updated_at):
        self.name = name
        self.slack_id = slack_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, name={self.name},, slack_id={self.slack_id}, created_at={self.created_at}, updated_at={self.updated_at}"

    @classmethod
    def select_users(cls):
        return cls.query.with_entities(
            cls.id, cls.name, cls.slack_id
        ).all()

    @classmethod
    def insert_user(self):
        db.session.add(self)



