import json
import os
import mysql.connector as mydb
from datetime import datetime
from flask import Blueprint, request, abort, jsonify
from flaskr.database import db
from flaskr.api.v1.slack.models import Message

api_v1_slack_bp = Blueprint('apiv1_slack', __name__, url_prefix='/api/v1/slack')


@api_v1_slack_bp.route('/message', methods=['POST'])
def get_slack_message():
    raw_data = request.get_data()
    message_data = json.loads(raw_data.decode(encoding='utf-8'))
    db_conn = mydb.connect(
        host=os.getenv('DB_HOST', os.environ['DB_HOSTNAME']),
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

    db_cur.execute("INSERT INTO messages(team_id, event_id, event_type, user_id, event_time, message_time, channel, text, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                   (message_data['team_id'], message_data['event_id'], message_data['event']['type'], message_data['event']['user'], message_data['event_time'], message_data['event']['event_ts'], message_data['event']['channel'], message_data['event']['text'], datetime.now(), datetime.now()))
    db_cur.close()
    db_conn.commit()
    db_conn.close()


    # message = Message(
    #     team_id=message_data['team_id'],
    #     event_id=message_data['event_id'],
    #     event_type=message_data['event']['type'],
    #     user_id=message_data['event']['user'],
    #     event_time=int(message_data['event_time']),
    #     message_time=float(message_data['event']['event_ts']),
    #     channel=message_data['event']['channel'],
    #     text=message_data['event']['text'],
    #     created_at=datetime.now(),
    #     updated_at=datetime.now()
    # )
    # message = Message(message_data['team_id'], message_data['event_id'], message_data['event']['type'], message_data['event']['user'], int(message_data['event_time']), float(message_data['event']['event_ts']), message_data['event']['channel'], message_data['event']['text'], datetime.now(), datetime.now())
    #
    # print(message)
    # with db.session.begin(subtransactions=True):
    #     message.insert_message()
    # db.session.commit()
    response = raw_data
    return response
