import os
import mysql.connector as mydb
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
    Migrate(app, db)


def connect_db():
    if os.environ['DB_HOSTNAME'] is None:
        db_conn = mydb.connect(
            user='root',
            password='password',
            database='mfos-db',
            port=3306
        )
        
    else:
        db_conn = mydb.connect(
            host=os.getenv(os.environ['DB_HOSTNAME']),
            user=os.getenv(os.environ['DB_USERNAME']),
            password=os.getenv(os.environ['DB_PASSWORD']),
            database=os.getenv(os.environ['DB_NAME']),
            port=3306
        )
        # db_conn = mydb.connect(
        #     host=os.getenv('DB_HOST', os.environ['DB_HOSTNAME']),
        #     user=os.getenv('DB_USER', os.environ['DB_USERNAME']),
        #     password=os.getenv('DB_PASSWORD', os.environ['DB_PASSWORD']),
        #     database=os.getenv('DB_NAME', os.environ['DB_NAME']),
        #     port=3306
        # )
    # except KeyError:

    return db_conn
