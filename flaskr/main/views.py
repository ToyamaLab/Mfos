import json
import mysql.connector as mydb
from flask import Blueprint, render_template, request
from datetime import datetime
from flaskr.main.models import (
    User
)

main_bp = Blueprint('main', __name__, template_folder='templates')


@main_bp.route('/')
def top_menu():
    users = User.select_users()
    return render_template(
        'main/top.html',
        users=users
    )


@main_bp.route('/user/post', methods=['POST'])
def get_slack_message():
    user_data = json.loads(request.get_data().decode(encoding='utf-8'))
    db_conn = mydb.connect(
        user=os.getenv('DB_USER', os.environ['DB_USERNAME']),
        password=os.getenv('DB_PASSWORD', os.environ['DB_PASSWORD']),
        database=os.getenv('DB_NAME', os.environ['DB_NAME']),
        port=3306
        # user='root',
        # password='password',
        # database='mfos-db',
        # port=3306
    )
    db_cur = db_conn.cursor()

    db_cur.execute("INSERT INTO users(name, slack_id, created_at, updated_at) VALUES(%s, %s, %s, %s)", (user_data['name'], user_data['slack_id'], datetime.now(), datetime.now()))
    db_cur.close()
    db_conn.commit()
    db_conn.close()

    user = User(
        name=user_data['name'],
        slack_id=user_data['slack_id'],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    print(user)
    # with db.session.begin(subtransactions=True):
    #     user.insert_user()
    # db.session.commit()
    response = user_data
    return response