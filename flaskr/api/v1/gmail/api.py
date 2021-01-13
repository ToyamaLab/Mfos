import os
import datetime
import pickle
import re
import email
import base64
import calendar
from flask import Blueprint
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from flaskr.api.v1.account_management import gmail_account_management
from datetime import datetime as dt
from flaskr.api.v1.gmail import (
    User,
    Mail,
)

api_v1_gmail_bp = Blueprint('apiv1_gmail', __name__, url_prefix='/api/v1/gmail')
KEY_FILE_LOCATION = 'credentials_gmail.json'
GOOGLE_GMAIL_ID = 'kazu.db.write@gmail.com'
GOOGLE_GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.modify",
]


def initialize_gmail():
    """
        作成者: kazu
        概要: googleの認証を行い,　APIを使用可能にする関数
    """
    credentials = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            credentials = gmail_account_management(GOOGLE_GMAIL_SCOPES)
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
    return build('gmail', 'v1', credentials=credentials, cache_discovery=False)


@api_v1_gmail_bp.route('/regist', methods=['POST'])
def regist_gmail():
    """
        作成者: kazu
        概要: Gmail APIを用いてgmail情報を抽出し, データベースへ保存する関数
    """
    gmail = initialize_gmail()
    message_list = []

    query = 'after:' + str(datetime.date.today() + datetime.timedelta(days=-30)) + ' before:' + str(
        datetime.date.today() + datetime.timedelta(days=1))

    message_id_list = gmail.users().messages().list(userId=GOOGLE_GMAIL_ID, maxResults=100, q=query).execute()
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
                message_data['date'] = dt.strptime(date_str, '%Y-%m-%d %H:%M:%S')
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
        if user_id_data: # 送信者のメールアドレスより, user_idを取得
            message_data['user_id'] = user_id_data[0]
        else:
            message_data['user_id'] = None

        message_list.append(message_data)

    target_list = Mail.check_duplicate(message_list)  # gmailテーブル内のデータに既に保存されていないか重複を確認
    Mail.insert_mail(target_list)
    response = {
        'status': 200,
        'data': target_list
    }

    return response
