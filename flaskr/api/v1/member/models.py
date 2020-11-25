from sqlalchemy import CheckConstraint
from datetime import datetime
from flaskr.database import db


class Information(db.Model):
    __tablename__ = 'e_information'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    department = db.Column(db.String(30), index=True, nullable=False)
    age = db.Column(db.Inteher, nullable=False)
    sex = db.Column(db.String(5), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, department, age, sex, created_at, updated_at):
        self.department = department
        self.age = age
        self.sex = sex
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, department = {self.department}, age = {self.age}, sex = {self.sex}, create_at={self.created_at}, update_at={self.updated_at} "

    @classmethod
    def insert_message(self):
        print(self.created_at)
        db.session.add(self)