import os
import datetime
import pickle
import re
import calendar
from flask import Blueprint
from apiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from flaskr.database import connect_db
from datetime import datetime as dt
from flaskr.api.v1.gmail.models import Mail

api_v1_gmail_bp = Blueprint('apiv1_gmail', __name__, url_prefix='/api/v1/gmail')
KEY_FILE_LOCATION = 'credentials_gmail.json'
# GOOGLE_GMAIL_ID = 'mfos-ml@gmailgroups.com'
GOOGLE_GMAIL_ID = 'kazu.db.write@gmail.com'
GOOGLE_GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.modify",
]


def initialize_gmail():
    credentials = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(KEY_FILE_LOCATION, GOOGLE_GMAIL_SCOPES)
            credentials = flow.run_console()
        with open("token.pickle", "wb") as token:
            pickle.dump(credentials, token)
    return build('gmail', 'v1', credentials=credentials, cache_discovery=False)


@api_v1_gmail_bp.route('/get', methods=['GET'])
def get_calendar():
    gmail = initialize_gmail()
    MessageList = []

    query = 'after:' + str(datetime.date.today() + datetime.timedelta(days=-10)) + ' before:' + str(
        datetime.date.today() + datetime.timedelta(days=1))

    messageIDlist = gmail.users().messages().list(userId=GOOGLE_GMAIL_ID, maxResults=100, q=query).execute()
    if messageIDlist['resultSizeEstimate'] == 0:
        print("Message is not found")
        return MessageList
    for message in messageIDlist['messages']:
        row = {}
        row['ID'] = message['id']
        MessageDetail = gmail.users().messages().get(userId='me', id=message['id']).execute()
        for header in MessageDetail['payload']['headers']:
            if header['name'] == 'Date':
                row['Date'] = header['value']
            elif header['name'] == 'From':
                row['From'] = header['value']
            elif header['name'] == 'Subject':
                row['Subject'] = header['value']
        MessageList.append(row)

    db_conn = connect_db()
    db_cur = db_conn.cursor()

    for message in MessageList:
        sender = message['From']
        sender_name = re.findall('".*"', sender)[0].strip('"')
        sender_email = re.findall('<.*>', sender)[0].strip('<').strip('>')

        date_data = message['Date'].split()
        months = {}
        for i, v in enumerate(calendar.month_abbr):
            months[v] = i
        date_str = date_data[3] + "-" + str(months[date_data[2]]) + "-" + date_data[1] + " " + date_data[4]
        date = dt.strptime(date_str, '%Y-%m-%d %H:%M:%S')

        db_cur.execute(
            "INSERT INTO gmail(message_id, sender_name, sender_email, date, message,  created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s)",
            (message['ID'], sender_name, sender_email, date, message['Subject'], dt.now(), dt.now()))

    response = {
        'status': 200
    }

    db_cur.close()
    db_conn.commit()
    db_conn.close()

    return response
