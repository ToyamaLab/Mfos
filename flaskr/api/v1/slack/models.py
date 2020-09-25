from sqlalchemy import CheckConstraint
from datetime import datetime
from flaskr.database import db


class Message(db.Model):
    __tablename__ = 'messages'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    team_id = db.Column(db.String(20), index=True, nullable=False)
    event_id = db.Column(db.String(20), nullable=False)
    event_type = db.Column(db.String(20), index=True, nullable=False)
    user_id = db.Column(db.String(20), index=True)
    event_time = db.Column(db.Integer, nullable=False)
    message_time = db.Column(db.Float(10))
    channel = db.Column(db.String(20), index=True)
    text = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, team_id, event_id, event_type, user_id, event_time, message_time, channel, text, created_at,
                 updated_at):
        self.team_id = team_id
        self.event_id = event_id
        self.event_type = event_type
        self.user_id = user_id
        self.event_time = event_time
        self.message_time = message_time
        self.channel = channel
        self.text = text
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, team_id={self.team_id}, event_id={self.event_id}, event_type={self.event_type}, " \
               f"user_id={self.user_id}, event_time={self.event_time}, message_time={self.message_time}, " \
               f"channel={self.channel}, text={self.text}, create_at={self.created_at}, update_at={self.updated_at} "

    @classmethod
    def insert_message(self):
        print(self.created_at)
        db.session.add(self)
