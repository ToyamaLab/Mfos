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
    create_at = db.Column(db.DateTime)
    update_at = db.Column(db.DateTime)

    def __init__(self, name, department, create_at, update_at):
        self.name = name
        self.department = department
        self.create_at = create_at
        self.update_at = update_at

    def __str__(self):
        return f"id = {self.id}, name={self.name}, department={self.department}, create_at={self.create_at}, update_at={self.update_at}"

    @classmethod
    def select_employees(cls):
        return cls.query.with_entities(
            cls.id, cls.name, cls.department
        ).all()
