import json
from flask import Blueprint, request
from flaskr.api.v1.slack import (
    User,
    SlackChannel,
    SlackChannelMember,
    SlackMessage,
)

api_v1_slack_bp = Blueprint('apiv1_slack', __name__, url_prefix='/api/v1/slack')


@api_v1_slack_bp.route('/message', methods=['POST'])
def get_slack_message():
    raw_data = request.get_data()
    message_data = json.loads(raw_data.decode(encoding='utf-8'))
    print(message_data)

    try:
        if message_data['event']['type'] == 'channel_created':
            user_id = User.check_user_slack_id(message_data['authed_users'][0])[0]
            SlackChannel.insert_channel(message_data['event']['channel']['id'], message_data['event']['channel']['name'])
            channel_id = SlackChannel.select_channel_id(message_data['event']['channel']['id'])[0]
            result = SlackMessage.insert_message_channel(user_id, channel_id, message_data)
        elif message_data['event']['type'] == 'channel_rename':
            user_id = User.check_user_slack_id(message_data['authed_users'][0])[0]
            channel_id = SlackChannel.select_channel_id(message_data['event']['channel']['id'])[0]
            SlackChannel.update_channel_name(message_data['event']['channel']['id'], message_data['event']['channel']['name'])
            result = SlackMessage.insert_message_channel(user_id, channel_id, message_data)
        elif message_data['event']['type'] == ('file_created' or 'file_shared' or 'file_deleted' or 'file_unshared' or 'file_change' or 'file_public'):
            user_id = User.check_user_slack_id(message_data['authed_users'][0])[0]
            result = SlackMessage.insert_message_file(user_id, message_data)
        elif message_data['event']['type'] == ('reaction_added' or 'reaction_removed'):
            user_id = User.check_user_slack_id(message_data['event']['item_user'])[0]
            channel_id = SlackChannel.select_channel_id(message_data['event']['item']['channel'])[0]
            result = SlackMessage.insert_message_reaction(user_id, channel_id, message_data)
        elif message_data['event']['type'] == 'message':
            print("1")
            user_id = User.check_user_slack_id(message_data['event']['user'])[0]
            print("2")
            channel_id = SlackChannel.select_channel_id(message_data['event']['channel'])[0]
            print("3")
            result = SlackMessage.insert_message(user_id, channel_id ,message_data)
        elif message_data['event']['type'] == 'member_joined_channel':
            user_id = User.check_user_slack_id(message_data['event']['user'])[0]
            channel_id = SlackChannel.select_channel_id(message_data['event']['channel'])[0]
            result = SlackMessage.insert_message_join(user_id, channel_id, message_data)

        # try:
        #     SlackChannelMember.insert_channel_member(user_id, channel_id)
        # except Exception:
        #     print('non member regist')

        response ={
            'status': 200,
            'data': result
        }
    except Exception as e:
        response = {
            'status': 'error',
            'error': e
        }

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
    print(response)
    return response
