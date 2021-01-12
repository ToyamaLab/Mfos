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
    """
        作成者: kazu
        概要: Slack Event APIより送信されたHTTPリクエストを処理するメソッド
        基本的な考え方:
            チャネル名の変更,メッセージ（テキスト形式・ファイル形式）, ファイルの削除に対応して適切な処理を行う.
    """
    raw_data = request.get_data()
    message_data = json.loads(raw_data.decode(encoding='utf-8'))

    try:
        if message_data['event']['type'] == 'channel_rename':  # チャネル名変更
            channel_id_data = SlackChannel.select_channel_id(message_data['event']['channel']['id'])
            if not channel_id_data:  # slack_channelsテーブルに一致するチャネル情報が存在しない場合
                SlackChannel.insert_channel(message_data['event']['channel']['id'],
                                            message_data['event']['channel']['name'])
            else:  # slack_channelsテーブルに一致するチャネル情報が存在する場合
                SlackChannel.update_channel_name(message_data['event']['channel']['id'],
                                             message_data['event']['channel']['name'])

        elif message_data['event']['type'] == 'file_deleted':  # ファイル削除
            try:
                file_id = message_data['event']['file_id']
                SlackMessage.delete_file(file_id)
            except Exception:
                return {
                    'status': 'error',
                    'error': 'the file is not registered'
                }

        elif message_data['event']['type'] == 'message':  # メッセージ
            if SlackMessage.check_duplicate(message_data):  # 同一イベントの重複処理を防ぐ
                return {
                    'status': 'error',
                    'error': 'The event is already exist.'
                }
            if 'text' in message_data['event']:  # テキスト情報が含まれる場合のみ処理する
                user_id = User.check_user_slack_id(message_data['event']['user'])[0]
                channel_id_data = SlackChannel.select_channel_id(message_data['event']['channel'])
                if not channel_id_data:  # チャネル情報がslack_chnnelsテーブル内のデータと一致しない場合, チャネル情報を保存する.
                    SlackChannel.insert_channel(message_data['event']['channel'], None)
                channel_id = SlackChannel.select_channel_id(message_data['event']['channel'])[0]
                SlackMessage.insert_message(user_id, channel_id, message_data)
                exist = SlackChannelMember.check_by_ids(user_id, channel_id)
                if not exist:  # ユーザーのチャネル所属関係がslack_channel_membersに保存されていない場合
                    SlackChannelMember.insert_channel_member(user_id, channel_id)
            else:
                return {
                        'status': 'error',
                        'error': 'text is not exist.'
                    }

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
