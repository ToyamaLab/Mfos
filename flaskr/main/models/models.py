import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, CheckConstraint
from flaskr.database import db


class Employees(db.Model):
    __tablename__ = 'employees'
    __table_args__ = (
        CheckConstraint('update_at >= create_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True)  # 主キー
    name = db.Column(db.String(20), index=True, nullable=False)  # デフォルト値
    department = db.Column(db.String(30), nullable=False)
    slack_id = db.Column(db.String(20), index=True)
    create_at = db.Column(db.DateTime)
    update_at = db.Column(db.DateTime)

    def __init__(self, name, department, create_at, update_at):
        self.name = name
        self.department = department
        self.slack_id = slack_id
        self.create_at = create_at
        self.update_at = update_at

    def __str__(self):
        return f"id = {self.id}, name={self.name}, department={self.department}, slack_id={self.slack_id}, create_at={self.create_at}, update_at={self.update_at}"

    @classmethod
    def select_employees(cls):
        return cls.query.with_entities(
            cls.id, cls.name, cls.department, cls.slack_id
        ).all()


class Actions(db.Model):
    __tablename__ = 'actions'
    __table_args__ = (
        CheckConstraint('update_at >= create_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True)  # 主キー
    team_id = db.Column(db.String(20), index=True, nullable=False)
    event_id = db.Column(db.String(20), nullable=False)
    event_type = db.Column(db.String(20), index=True, nullable=False)
    user_id = db.Column(db.String(20), index=True)
    event_time = db.Column(db.Integer, nullable=False)
    message_time = db.Column(db.Float(10))
    channel = db.Column(db.String(20), index=True)
    text = db.Column(db.String(300))
    create_at = db.Column(db.DateTime)
    update_at = db.Column(db.DateTime)

    def __init__(self, team_id, event_id, event_type, user_id, event_time, message_time, channel, text, create_at,
                 update_at):
        self.team_id = team_id
        self.event_id = event_id
        self.event_type = event_type
        self.user_id = user_id
        self.event_time = event_time
        self.message_time = message_time
        self.channel = channel
        self.text = text
        self.create_at = create_at
        self.update_at = update_at

    def __str__(self):
        return f"id = {self.id}, team_id={self.team_id}, event_id={self.event_id}, event_type={self.event_type}, user_id={self.user_id}, event_time={self.event_time}, message_time={self.message_time}, channel={self.channel}, text={self.text}, create_at={self.create_at}, update_at={self.update_at}"

    @classmethod
    def insert_action(self):
        db.session.add(self)
