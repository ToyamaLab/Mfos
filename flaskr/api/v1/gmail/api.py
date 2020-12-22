import os
import datetime
import pickle
import re
import email
import base64
import calendar
from flask import Blueprint
from apiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
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
    results = []

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
        print(MessageDetail)
        for header in MessageDetail['payload']['headers']:
            if header['name'] == 'Date':
                row['Date'] = header['value']
            elif header['name'] == 'From':
                row['From'] = header['value']
            elif header['name'] == 'Subject':
                row['Subject'] = header['value']
        MessageDetail = gmail.users().messages().get(userId="me", id=message["id"], format="full").execute()
        if MessageDetail["payload"]["mimeType"] == "multipart/alternative":
            for payload_parts in MessageDetail["payload"]["parts"]:
                if payload_parts["mimeType"] == "text/plain":
                    for payload_header in payload_parts["headers"]:
                        if payload_header["name"] == "Content-Type" and payload_header["value"].lower() == "text/plain; charset=utf-8":
                            row["Body"] = email.message_from_string(
                                str(base64.urlsafe_b64decode(payload_parts["body"]["data"]), "utf-8")).get_payload()
        MessageList.append(row)

    for message in MessageList:
        sender = message['From']
        sender_name = re.split('<', sender)[0]
        sender_email = re.findall('<.*>', sender)[0].strip('<').strip('>')

        date_data = message['Date'].split()
        months = {}
        for i, v in enumerate(calendar.month_abbr):
            months[v] = i
        date_str = date_data[3] + "-" + str(months[date_data[2]]) + "-" + date_data[1] + " " + date_data[4]
        date = dt.strptime(date_str, '%Y-%m-%d %H:%M:%S')

        try:
            print(sender_email)
            user_id = User.check_user_mail(sender_email)[0]
            Mail.insert_mail(user_id, message, sender_name, sender_email, date)
            result = {}
            result['user_id'] = user_id
            result['message_id'] = message['ID']
            result['sender_name'] = sender_name
            result['sender_email'] = sender_email
            result['date'] = date
            result['subject'] = message['Subject']
            # result['message'] = message['Body']
            results.append(result)
        except Exception:
            print('Error')

    response = {
        'status': 200,
        'result': results
    }

    return response
