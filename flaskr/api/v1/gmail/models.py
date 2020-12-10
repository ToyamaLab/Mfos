from sqlalchemy import CheckConstraint
from datetime import datetime
from flaskr.database import db


class Mail(db.Model):
    __tablename__ = 'gmail'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    message_id = db.Column(db.String(50), nullable=False)
    sender_name = db.Column(db.String(50), nullable=False)
    sender_email = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.String(2000))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, message_id, sender_name, sender_email, date, message, created_at, updated_at):
        self.message_id = message_id
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.date = date
        self.message = message
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, message_id = {self.message_id}, sender_name = {self.sender_name}, sender_email = {self.sender_email}, date = {self.date}, message = {self.message}, create_at={self.created_at}, update_at={self.updated_at} "

    @classmethod
    def insert_message(self):
        print(self.created_at)
        db.session.add(self)