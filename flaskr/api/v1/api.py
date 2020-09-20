import json
from datetime import datetime
from flask import Blueprint, request, abort, jsonify
from flaskr.database import db
from flaskr.main.models import Actions

api_v1_bp = Blueprint('apiv1', __name__, url_prefix='/api/v1')


@api_v1_bp.route('/slack', methods=['POST'])
def get_slack_action():
    action_data = json.loads(request.get_data().decode(encoding='utf-8'))
    print(action_data['team_id'])
    action = Actions(
        team_id=action_data['team_id'],
        event_id=action_data['event_id'],
        event_type=action_data['event']['type'],
        user_id=action_data['event']['user'],
        event_time=int(action_data['event_time']),
        message_time=float(action_data['event']['event_ts']),
        channel=action_data['event']['channel'],
        text=action_data['event']['text'],
        create_at=datetime.now(),
        update_at=datetime.now()
    )
    print(action)
    with db.session.begin(subtransactions=True):
        action.insert_action()
    db.session.commit()
    response = action_data
    return response
