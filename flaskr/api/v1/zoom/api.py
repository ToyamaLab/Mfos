import base64
import os
import json
import http.client
from flask import Blueprint
from flaskr.api.v1.account_management import zoom_account_management
from flaskr.api.v1.zoom import (
    User,
    ZoomAccessToken,
    ZoomMeeting,
    ZoomParticipant,
)

api_v1_zoom_bp = Blueprint('apiv1_zoom', __name__, url_prefix='/api/v1/zoom')
conn = http.client.HTTPSConnection("api.zoom.us")
conn_token = http.client.HTTPSConnection("zoom.us")
accounts = zoom_account_management()


def refresh_token(user_id):
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
    results_meeting = []
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
        print(meetings)
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
        print(meetings)
        headers = headers_updated

    new_meeting_uuids = []

    for meeting in meetings:
        meeting['start_time'] = meeting['start_time'].replace('T', ' ').replace('Z', '')
        meeting['created_at'] = meeting['created_at'].replace('T', ' ').replace('Z', '')
        new_meeting_uuids.append(meeting['uuid'])
        try:
            user_id = User.check_user_mail(accounts['zoom_user_id'])[0]
            print(user_id)
            ZoomMeeting.insert_schedule(user_id, meeting)
            result = {}
            result['user_id'] = user_id
            result['meeting_id'] = meeting['id']
            result['meeting_uuid'] = meeting['uuid']
            result['topic'] = meeting['topic']
            result['start_time'] = meeting['start_time']
            result['duration'] = meeting['duration']
            results_meeting.append(result)
        except Exception:
            print('Error')

    # db_cur.close()

    # conn2 = http.client.HTTPSConnection("api.zoom.us")
    # targets = []
    # results_participant = []
    #
    # for new_meeting_uuid in new_meeting_uuids:
    #     target = {}
    #     conn2.request("GET", "/v2/past_meetings/" + str(new_meeting_uuid) + "/participants?page_size=200", headers=headers)
    #     res = conn2.getresponse()
    #     data = res.read().decode("utf-8")
    #     data_json = json.loads(data)
    #     print(data_json)
    #     participants = data_json['participants']
    #     target['uuid'] = new_meeting_uuid
    #     target['participants'] = participants
    #     targets.append(target)
    #
    # # db_cur2 = db_conn.cursor()
    # for i in range(len(targets)):
    #     participants = targets[i]['participants']
    #     meeting_uuid = targets[i]['uuid']
    #     meeting_id = ZoomMeeting.check_meeting_uuid(meeting_uuid)
    #     for participant in participants:
    #         try:
    #             user_id = User.check_user_mail(participant['user_email'])[0]
    #             ZoomParticipant.insert_participant(user_id, meeting_id, participant)
    #             result = {}
    #             result['user_id'] = user_id
    #             result['meeting_id'] = meeting_id
    #             result['zoom_user_id'] = participants['id']
    #             result['zoom_name'] = participants['name']
    #             results_participant.append(result)
    #         except Exception:
    #             print('Error')

    # db_cur2.close()
    # db_conn.commit()
    # db_conn.close()

    # {"page_size": 100, "total_records": 1, "next_page_token": "", "meetings": [
    #     {"uuid": "bv3rEDQ9QS2WziD1IlcMTA==", "id": 77954320276, "host_id": "0K1kr54YTpOGQBDdWXXloQ", "topic": "test",
    #      "type": 2, "start_time": "2020-12-13T15:00:00Z", "duration": 60, "timezone": "Asia/Tokyo",
    #      "created_at": "2020-12-13T14:33:55Z",
    #      "join_url": "https://us04web.zoom.us/j/77954320276?pwd=cGhPQTkyVHhXZUpCWi9hbUEyZU1LQT09"}]}

    # results = []
    # results.append(results_meeting)
    # results.append(results_participant)
    response = {
        'status': 200,
        'data': results_meeting
    }

    return response


# @api_v1_zoom_bp.route('/get/messages', methods=['GET'])
# def get_messages():
#     user_id = User.check_user_mail(account.userId)[0]
#     headers = {
#         'Host': 'api.zoom.us',
#         'Authorization': "Bearer " + ZoomAccessToken.get_access_token(user_id)[0],
#         'content-type': "application/json"
#     }
#     channel = 'tdPeVcJPRkqgULIzult3Zw=='
#     conn.request("GET", "/v2/chat/users/" + account.userId + "/messages?page_size=50&to_channel=" + channel , headers=headers)
#
#     res = conn.getresponse()
#     data = res.read()
#
#     print(data.decode("utf-8"))
#
#     response = {
#         'status': 200
#     }
#
#     return response


# @api_v1_zoom_bp.route('/get/recordings', methods=['GET'])
# def get_recordings():
#     results = []
#     user_id = User.check_user_mail(account.userId)[0]
#     try:
#         headers = {
#             'Host': 'api.zoom.us',
#             'Authorization': "Bearer " + ZoomAccessToken.get_access_token(user_id)[0],
#             'content-type': "application/json"
#         }
#         conn.request("GET", "/v2/users/" + account.userId + "/recordings?page_size=200" , headers=headers)
#         res = conn.getresponse()
#         data = res.read().decode("utf-8")
#         data_json = json.loads(data)
#         print(data.decode("utf-8"))
#     except Exception:
#         refresh_token(db_conn, user_id)
#         headers_updated = {
#             'Host': 'api.zoom.us',
#             'Authorization': "Bearer " + ZoomAccessToken.get_access_token(user_id)[0],
#             'content-type': "application/json"
#         }
#         conn.request("GET", "/v2/users/" + account.userId + "/recordings?page_size=200", headers=headers_updated)
#         res = conn.getresponse()
#         data = res.read()
#         print(data.decode("utf-8"))
#
#
#     response = {
#         'status': 200
#     }
#
#     return response
