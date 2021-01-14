import os
import datetime
import calendar
import re
import json
import pickle
from flask import Blueprint, request
from flaskr.database import db
from flaskr.main.models import (
    User,
    Information,
    Mail,
    Calendar,
    SlackChannelMember,
    SlackChannel,
    SlackMessage,
    ZoomMeeting
)

verification_bp = Blueprint('apiv1_verification', __name__, url_prefix='/verification')


@verification_bp.route('/mfos/information', methods=['GET'])
def verification_information_mfos():
    users_data = db.session.query(User, Information).join(Information, User.id == Information.user_id).with_entities(User.id, User.gmail, Information.name, Information.department).all()
    response = []
    for user in users_data:
        data = {'id': user[0], 'mail':user[1], 'name':user[2], 'department':user[3]}
        response.append(data)
    return {
        'result': response
    }

@verification_bp.route('/mfos/gmail', methods=['GET'])
def verification_gmail_mfos():
    users_data = db.session.query(User, Mail).join(Mail, User.id == Mail.user_id).with_entities(User.id, User.gmail, User.slack_id, Mail.subject, Mail.message_id).all()
    response = []
    for user in users_data:
        data = {'id': user[0], 'mail':user[1], 'slack':user[2], 'subject':user[3], 'message_id':user[4]}
        response.append(data)
    return {
        'result': response
    }

@verification_bp.route('/mfos/schedule', methods=['GET'])
def verification_schedule_mfos():
    users_data = db.session.query(User, Calendar).join(Calendar, User.id == Calendar.user_id).with_entities(User.id, User.gmail, User.slack_id, Calendar.title).all()
    response = []
    for user in users_data:
        data = {'id': user[0], 'mail':user[1], 'slack':user[2], 'title':user[3]}
        response.append(data)
    return {
        'result': response
    }

@verification_bp.route('/mfos/zoom', methods=['GET'])
def verification_zoom_mfos():
    users_data = db.session.query(User, ZoomMeeting).join(ZoomMeeting, User.id == ZoomMeeting.user_id).with_entities(User.id, User.gmail, User.slack_id, ZoomMeeting.topic).all()
    response = []
    for user in users_data:
        data = {'id': user[0], 'mail':user[1], 'slack':user[2], 'topic':user[3]}
        response.append(data)
    return {
        'result': response
    }

@verification_bp.route('/mfos/slack', methods=['GET'])
def verification_slack_mfos():
    users_data = db.session.query(User, SlackMessage).join(SlackMessage, User.id == SlackMessage.user_id).with_entities(User.id, User.gmail, User.slack_id, SlackMessage.event_id).all()
    response = []
    for user in users_data:
        data = {'id': user[0], 'mail':user[1], 'slack':user[2], 'event_id':user[3]}
        response.append(data)
    return {
        'result': response
    }

@verification_bp.route('/mfos/gmail/schedule', methods=['GET'])
def verification_schedule_gmail_mfos():
    mail = request.args.get('mail')

    gmail = db.session.query(User, Mail).join(Mail, User.id == Mail.user_id).filter(User.gmail == mail).with_entities(User.id, User.gmail, User.slack_id, Mail.subject, Mail.message_id).all()
    mails_data = []
    for g in gmail:
        mail_data = {'subject': g[3], 'message_id': g[4]}
        mails_data.append(mail_data)

    calendar = db.session.query(User, Calendar).join(Calendar, User.id == Calendar.user_id).filter(User.gmail == mail).with_entities(User.id, User.gmail, User.slack_id, Calendar.title).all()
    calendars_data = []
    for c in calendar:
        calendar_data = {'title': c[3]}
        calendars_data.append(calendar_data)

    response = {'mail': mails_data, 'calendar': calendars_data}
    return {
        'result': response
    }


@verification_bp.route('/mfos/info/gmail', methods=['GET'])
def verification_info_gmail_mfos():
    users_data = db.session.query(Mail, Information).join(Mail, Mail.user_id == Information.user_id).with_entities(Mail.subject, Information.name, Information.department).all()
    response = []
    for user in users_data:
        data = {'subject': user[0], 'name': user[1], 'department': user[2]}
        response.append(data)
    return {
        'result': response
    }


@verification_bp.route('/test1', methods=['GET'])
def verification_test1():
    from oauth2client.service_account import ServiceAccountCredentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])

    sheet = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
    search_query = sheet.spreadsheets().values().get(spreadsheetId='16a8Xq-lL6VVIQ_WToQZIntFfa3b5tmOIB91cY75N-YY', range="社員情報!A2:E2500").execute()
    targets = search_query['values']
    results = []
    errors = []

    for i in range(len(targets)):
        try:  # Spread Sheetへの記入を処理している. 記入が適切でない場合はその行に記入されているデータに関しては以降の処理を行わず, Gmailを戻す.
            information_data = {'gmail': targets[i][1], 'name': targets[i][0], 'department': targets[i][2]}
            results.append(information_data)
        except Exception:
            errors.append(targets[i][1])
            continue

    return {
        'result': results,
        'error': errors
    }


@verification_bp.route('/test2', methods=['GET'])
def verification_test2():
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request
    from oauth2client.service_account import ServiceAccountCredentials
    from google_auth_oauthlib.flow import InstalledAppFlow

    credentials = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials_gmail.json', ["https://www.googleapis.com/auth/gmail.compose", "https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.labels", "https://www.googleapis.com/auth/gmail.modify"])
            credentials = flow.run_console()
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
    gmail = build('gmail', 'v1', credentials=credentials, cache_discovery=False)

    message_list = []

    query = 'after:' + str(datetime.date.today() + datetime.timedelta(days=-30)) + ' before:' + str(
        datetime.date.today() + datetime.timedelta(days=1))

    message_id_list = gmail.users().messages().list(userId='kazu.db.write@gmail.com', maxResults=100, q=query).execute()
    if message_id_list['resultSizeEstimate'] == 0:
        return {
            'status': 200,
            'data': 'No new mail'
        }
    for message in message_id_list['messages']:
        message_data = {}
        message_data['id'] = message['id']
        MessageDetail = gmail.users().messages().get(userId='me', id=message['id']).execute()
        for header in MessageDetail['payload']['headers']:
            if header['name'] == 'Date':  # 日時情報
                date_data = header['value'].split()
                months = {}
                for i, v in enumerate(calendar.month_abbr):
                    months[v] = i
                date_str = date_data[3] + "-" + str(months[date_data[2]]) + "-" + date_data[1] + " " + date_data[4]
                message_data['date'] = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            elif header['name'] == 'From':  # 送信者情報
                message_data['sender_name'] = re.split('<', header['value'])[0]
                message_data['sender_email'] = re.findall('<.*>', header['value'])[0].strip('<').strip('>')
            elif header['name'] == 'Subject':  # タイトル情報
                message_data['subject'] = header['value']
        if 'snippet' in MessageDetail:  # 本文
            message_data['body'] = MessageDetail['snippet']
        else:
            message_data['body'] = None
        user_id_data = User.check_user_mail(message_data['sender_email'])
        if user_id_data:  # 送信者のメールアドレスより, user_idを取得
            message_data['user_id'] = user_id_data[0]
        else:
            message_data['user_id'] = None

        message_list.append(message_data)

    return {
        'result': message_list
    }


@verification_bp.route('/test3', methods=['GET'])
def verification_test3():
    from oauth2client.service_account import ServiceAccountCredentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', ['https://www.googleapis.com/auth/calendar.readonly'])

    calendar = build('calendar', 'v3', credentials=credentials, cache_discovery=False)

    events_result = calendar.events().list(
        calendarId='a1kaac9ee3r8i8l3phasc0tpq8@group.calendar.google.com',
        timeMin=(datetime.datetime.utcnow() + datetime.timedelta(days=-30)).isoformat() + "Z",
        timeMax=(datetime.datetime.utcnow() + datetime.timedelta(days=30)).isoformat() + "Z",
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        return {
            'status': 200,
            'data': 'No upcoming events found'
        }

    events_data = []
    for event in events:
        single_keys = ['id', 'htmlLink', 'summary', 'description', 'location']
        event_data = {}
        for key in single_keys:
            if key in event:
                event_data[key] = event[key]
            else:
                event_data[key] = None
        created_date = event['created'].replace('T', ' ').rstrip('Z')
        event_data['created'] = datetime.datetime.fromisoformat(created_date)
        updated_date = event['updated'].replace('T', ' ').rstrip('Z')
        event_data['updated'] = datetime.datetime.fromisoformat(updated_date)
        event_data['creator'] = event['creator']['email']
        if 'dateTime' in event['start']:
            event_data['all_day'] = False
            event_data['start'] = datetime.datetime.fromisoformat(event['start']['dateTime']).strftime("%Y/%m/%d %H:%M:%S.%f")
            event_data['end'] = datetime.datetime.fromisoformat(event['end']['dateTime']).strftime("%Y/%m/%d %H:%M:%S.%f")
            event_data['date'] = None
            event_data['sort_date'] = event_data['start']
        else:
            event_data['all_day'] = True
            event_data['start'] = None
            event_data['end'] = None
            event_data['date'] = event['start']['date']
            event_data['sort_date'] = event_data['date']
        events_data.append(event_data)

    return {
        'result': events_data
    }


@verification_bp.route('/test4', methods=['GET'])
def verification_test4(access_token, user_id):
    import http.client
    conn = http.client.HTTPSConnection("api.zoom.us")

    headers = {
        'Host': 'api.zoom.us',
        'Authorization': "Bearer " + access_token,
        'content-type': "application/json"
    }
    conn.request("GET", "/v2/users/" + user_id + "/meetings?page_size=100", headers=headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    data_json = json.loads(data)
    meetings = data_json['meetings']

    meeting_list = []
    for meeting in meetings:
        meeting_data = {}
        meeting_data['start_time'] = datetime.datetime.strptime(
            meeting['start_time'].replace('T', ' ').replace('Z', ''), '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=9)
        meeting_data['created_at'] = datetime.datetime.strptime(
            meeting['created_at'].replace('T', ' ').replace('Z', ''), '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=9)
        meeting_data['meeting_id'] = meeting['id']
        meeting_data['meeting_uuid'] = meeting['uuid']
        meeting_data['topic'] = meeting['topic']
        meeting_data['duration'] = meeting['duration']
        if User.check_user_mail(accounts['zoom_user_id']):
            meeting_data['user_id'] = User.check_user_mail(accounts['zoom_user_id'])[0]
        else:
            meeting_data['user_id'] = None
        meeting_list.append(meeting_data)

    return {
        'result': meeting_list
    }


@verification_bp.route('/test5', methods=['GET'])
def verification_test5():
    from oauth2client.service_account import ServiceAccountCredentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.auth.transport.requests import Request

    credentials = ServiceAccountCredentials.from_json_keyfile_name('credentials.json',
                                                                   ['https://spreadsheets.google.com/feeds',
                                                                    'https://www.googleapis.com/auth/drive'])

    sheet = build('sheets', 'v4', credentials=credentials, cache_discovery=False)
    search_query = sheet.spreadsheets().values().get(spreadsheetId='16a8Xq-lL6VVIQ_WToQZIntFfa3b5tmOIB91cY75N-YY',range="社員情報!A2:E2500").execute()
    targets = search_query['values']
    results = []
    errors = []

    for i in range(len(targets)):
        try:  # Spread Sheetへの記入を処理している. 記入が適切でない場合はその行に記入されているデータに関しては以降の処理を行わず, Gmailを戻す.
            information_data = {'gmail': targets[i][1], 'name': targets[i][0], 'department': targets[i][2], 'birthday': targets[i][3], 'sex': targets[i][4]}
            results.append(information_data)
        except Exception:
            errors.append(targets[i][1])
            continue



    credentials = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials_gmail.json',
                                                             ["https://www.googleapis.com/auth/gmail.compose",
                                                              "https://www.googleapis.com/auth/gmail.readonly",
                                                              "https://www.googleapis.com/auth/gmail.labels",
                                                              "https://www.googleapis.com/auth/gmail.modify"])
            credentials = flow.run_console()
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
    gmail = build('gmail', 'v1', credentials=credentials, cache_discovery=False)

    message_list = []

    query = 'after:' + str(datetime.date.today() + datetime.timedelta(days=-30)) + ' before:' + str(
        datetime.date.today() + datetime.timedelta(days=1))

    message_id_list = gmail.users().messages().list(userId='kazu.db.write@gmail.com', maxResults=100, q=query).execute()
    if message_id_list['resultSizeEstimate'] == 0:
        return {
            'status': 200,
            'data': 'No new mail'
        }
    for message in message_id_list['messages']:
        message_data = {}
        message_data['id'] = message['id']
        MessageDetail = gmail.users().messages().get(userId='me', id=message['id']).execute()
        for header in MessageDetail['payload']['headers']:
            if header['name'] == 'Date':  # 日時情報
                date_data = header['value'].split()
                months = {}
                for i, v in enumerate(calendar.month_abbr):
                    months[v] = i
                date_str = date_data[3] + "-" + str(months[date_data[2]]) + "-" + date_data[1] + " " + date_data[4]
                message_data['date'] = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            elif header['name'] == 'From':  # 送信者情報
                message_data['sender_name'] = re.split('<', header['value'])[0]
                message_data['sender_email'] = re.findall('<.*>', header['value'])[0].strip('<').strip('>')
            elif header['name'] == 'Subject':  # タイトル情報
                message_data['subject'] = header['value']
        if 'snippet' in MessageDetail:  # 本文
            message_data['body'] = MessageDetail['snippet']
        else:
            message_data['body'] = None
        user_id_data = User.check_user_mail(message_data['sender_email'])
        if user_id_data:  # 送信者のメールアドレスより, user_idを取得
            message_data['user_id'] = user_id_data[0]
        else:
            message_data['user_id'] = None

        message_data['user_name'] = None
        message_data['department'] = None
        message_data['birthday'] = None
        message_data['sex'] = None

        for result in results:
            if result['gmail'] == message_data['sender_email']:
                message_data['user_name'] = result['name']
                message_data['department'] = result['department']
                message_data['birthday'] = result['birthday']
                message_data['sex'] = result['sex']

        message_list.append(message_data)

    return {
        'result': message_list
    }
