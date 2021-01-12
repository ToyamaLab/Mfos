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
    channel_check = 0
    print(message_data)

    try:
        if message_data['event']['type'] == 'channel_created':
            user_id = User.check_user_slack_id(message_data['authed_users'][0])[0]
            SlackChannel.insert_channel(message_data['event']['channel']['id'],
                                        message_data['event']['channel']['name'])
            channel_id = SlackChannel.select_channel_id(message_data['event']['channel']['id'])[0]
            SlackMessage.insert_message_channel(user_id, channel_id, message_data)

        elif message_data['event']['type'] == 'channel_rename':
            print('aaa')
            user_id = User.check_user_slack_id(message_data['authed_users'][0])[0]
            print(user_id)
            channel_id_data = SlackChannel.select_channel_id(message_data['event']['channel']['id'])
            print(channel_id_data)
            if not channel_id_data:
                print('bbb')
                SlackChannel.insert_channel(message_data['event']['channel']['id'],
                                            message_data['event']['channel']['name'])
            else:
                print('ccc')
                SlackChannel.update_channel_name(message_data['event']['channel']['id'],
                                             message_data['event']['channel']['name'])
            print('ddd')
            channel_id = SlackChannel.select_channel_id(message_data['event']['channel']['id'])[0]
            print(channel_id)
            SlackMessage.insert_message_channel(user_id, channel_id, message_data)
            print('eee')

        elif message_data['event']['type'] == 'file_deleted':
            try:
                file_id = message_data['event']['file_id']
                SlackMessage.delete_file(file_id)
                channel_check = 1
            except Exception:
                return {
                    'status': 'error',
                    'error': 'the file is not registered'
                }

        elif message_data['event']['type'] == 'message':
            if 'text' in message_data['event']:
                user_id = User.check_user_slack_id(message_data['event']['user'])[0]
                channel_id_data = SlackChannel.select_channel_id(message_data['event']['channel'])
                if not channel_id_data:
                    SlackChannel.insert_channel(message_data['event']['channel'], None)
                channel_id = SlackChannel.select_channel_id(message_data['event']['channel'])[0]
                SlackMessage.insert_message(user_id, channel_id, message_data)
            else:
                return {
                        'status': 'error',
                        'error': 'text is not exist.'
                    }

        if channel_check == 0:
            exist = SlackChannelMember.check_by_ids(user_id, channel_id)
            if not exist:
                SlackChannelMember.insert_channel_member(user_id, channel_id)

        response = {
            'status': 200,
            'result': message_data
        }
    except Exception as e:
        response = {
            'status': 'error',
            'error': e
        }

    return response
