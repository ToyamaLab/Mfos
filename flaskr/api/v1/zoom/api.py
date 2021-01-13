import base64
import os
import datetime
import json
import http.client
from flask import Blueprint
from flaskr.api.v1.account_management import zoom_account_management
from flaskr.api.v1.zoom import (
    User,
    ZoomAccessToken,
    ZoomMeeting,
)

api_v1_zoom_bp = Blueprint('apiv1_zoom', __name__, url_prefix='/api/v1/zoom')
conn = http.client.HTTPSConnection("api.zoom.us")
conn_token = http.client.HTTPSConnection("zoom.us")
accounts = zoom_account_management()


def refresh_token(user_id):
    """
        作成者: kazu
        概要: Zoom APIへのリクエストに使うアクセストークンが期限切れになっていた場合に更新する関数
    """
    headers = {
        'host': 'zoom.us',
        'authorization': 'Basic ' + base64.b64encode((accounts['zoom_client_id'] + ":" + accounts['zoom_client_secret']).encode()).decode("ascii"),

    }
    refresh_token = ZoomAccessToken.get_refresh_token(user_id)[0].strip()
    conn_token.request("POST", "/oauth/token?grant_type=refresh_token&refresh_token=" + refresh_token, headers=headers)

    res = conn_token.getresponse()
    data = res.read().decode("utf-8")
    data_json = json.loads(data)
    access_token = data_json['access_token']
    refresh_token = data_json['refresh_token']
    ZoomAccessToken.update_access_token(user_id, access_token, refresh_token)


@api_v1_zoom_bp.route('/get/meetings', methods=['GET'])
def get_meetings():
    """
        作成者: kazu
        概要: Zoom APIより取得したミーティング情報をzoom_meetingsテーブルに保存する関数
        基本的な考え方:
            ミーティング情報をリストで取得した後、含まれているuuidで既にテーブルに保存されている情報かどうかを識別.
            既に保存されている場合は開始時間などが更新されている可能性があるため更新, 保存されていない場合は新規保存を行う.
    """
    user_id = User.check_user_mail(accounts['zoom_user_id'])[0]
    conn = http.client.HTTPSConnection("api.zoom.us")
    try:
        headers = {
            'Host': 'api.zoom.us',
            'Authorization': "Bearer " + ZoomAccessToken.get_access_token(user_id)[0],
            'content-type': "application/json"
        }
        conn.request("GET", "/v2/users/" + accounts['zoom_user_id'] + "/meetings?page_size=100", headers=headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        data_json = json.loads(data)
        meetings = data_json['meetings']
    except Exception:
        refresh_token(user_id)
        headers_updated = {
            'Host': 'api.zoom.us',
            'Authorization': "Bearer " + ZoomAccessToken.get_access_token(user_id)[0],
            'content-type': "application/json"
        }
        conn.request("GET", "/v2/users/" + accounts['zoom_user_id'] + "/meetings?page_size=100", headers=headers_updated)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        data_json = json.loads(data)
        meetings = data_json['meetings']

    meeting_list = []

    for meeting in meetings:
        meeting_data = {}
        meeting_data['start_time'] = datetime.datetime.strptime(meeting['start_time'].replace('T', ' ').replace('Z', ''), '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=9)
        meeting_data['created_at'] = datetime.datetime.strptime(meeting['created_at'].replace('T', ' ').replace('Z', ''), '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=9)
        meeting_data['meeting_id'] = meeting['id']
        meeting_data['meeting_uuid'] = meeting['uuid']
        meeting_data['topic'] = meeting['topic']
        meeting_data['duration'] = meeting['duration']
        if User.check_user_mail(accounts['zoom_user_id']):
            meeting_data['user_id'] = User.check_user_mail(accounts['zoom_user_id'])[0]
        else:
            meeting_data['user_id'] = None
        meeting_list.append(meeting_data)

    target = ZoomMeeting.check_duplicate(meeting_list)
    ZoomMeeting.insert_meeting(target['insert'])
    ZoomMeeting.update_meeting(target['update'])

    response = {
        'status': 200,
        'data': target
    }

    return response
