import datetime
from flask import Blueprint
from googleapiclient.discovery import build
from flaskr.api.v1.account_management import google_account_management
from flaskr.api.v1.calendar import (
    User,
    Calendar,
)

api_v1_calendar_bp = Blueprint('apiv1_calendar', __name__, url_prefix='/api/v1/calendar')
KEY_FILE_LOCATION = 'credentials.json'
GOOGLE_CALENDAR_ID = 'kazu.agestock@gmail.com'
GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
google_credentials = google_account_management(GOOGLE_CALENDAR_SCOPES)


def initialize_calendar():
    credentials = google_credentials
    return build('calendar', 'v3', credentials=credentials, cache_discovery=False)


@api_v1_calendar_bp.route('/regist', methods=['POST'])
def get_calendar():
    """
        作成者: kazu
        概要: Google Calendarの情報を保存するメソッド
        基本的な考え方:
            Google Calendar APIを利用し, 現在時刻より30日間の予定を取得.
            データベース内のデータと照合し, 新規保存や更新などを行う.
    """
    calendar = initialize_calendar()
    events_result = calendar.events().list(
        calendarId=GOOGLE_CALENDAR_ID,
        timeMin=datetime.datetime.utcnow().isoformat()+"Z",
        timeMax=(datetime.datetime.utcnow() + datetime.timedelta(days=30)).isoformat()+"Z",
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

        if Calendar.check_schedule_event_id(event_data['id']):
            Calendar.update_schedule(event_data)
        else:
            user_id = User.check_user_mail(event_data['creator'])[0]
            Calendar.insert_schedule(user_id, event_data)

    response = {
        'status': 200,
        'data': events_data
    }

    return response
