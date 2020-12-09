from sqlalchemy import CheckConstraint
from datetime import datetime
from flaskr.database import db


class Calendar(db.Model):
    __tablename__ = 'schedule'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    event_id = db.Column(db.String(50), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    event_created = db.Column(db.DateTime, nullable=False)
    event_updated = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(400))
    location = db.Column(db.String(50))
    creator = db.Column(db.String(50), nullable=False)
    all_day = db.Column(db.Boolean, nullable=False, default=False)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, event_id, link, event_created, event_updated, title, description, location, creator, start, end, date, created_at, updated_at):
        self.event_id = event_id
        self.link = link
        self.event_created = event_created
        self.event_updated = event_updated
        self.title = title
        self.description = description
        self.location = location
        self.creator = creator
        self.start = start
        self.end = end
        self.date = date
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, event_id = {self.event_id}, link = {self.link}, event_created = {self.event_created}, event_updated = {self.event_updated}, title = {self.title}, description = {self.description}, location = {self.location}, creator = {self.creator}, start = {self.start}, end = {self.end}, date = {self.date}, create_at={self.created_at}, update_at={self.updated_at} "

    @classmethod
    def insert_message(self):
        print(self.created_at)
        db.session.add(self)