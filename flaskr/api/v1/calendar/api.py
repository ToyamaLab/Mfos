import datetime
from flask import Blueprint
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
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


@api_v1_calendar_bp.route('/get', methods=['GET'])
def get_calendar():
    calendar = initialize_calendar()
    events_result = calendar.events().list(
        calendarId=GOOGLE_CALENDAR_ID,
        timeMin=datetime.datetime.now().isoformat()+"Z",
        timeMax=(datetime.datetime.now() + datetime.timedelta(days=10)).isoformat()+"Z",
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    results = []

    if not events:
        print('No upcoming events found')

    events_data = []
    for event in events:
        single_keys = ['id', 'htmlLink', 'summary', 'description', 'location']
        event_data=[]
        for key in single_keys:
            if key in event:
                event_data.append(event[key])
            else:
                event_data.append('')
        created_date = event['created'].replace('T', ' ').rstrip('Z')
        created = datetime.datetime.fromisoformat(created_date)
        updated_date = event['updated'].replace('T', ' ').rstrip('Z')
        updated = datetime.datetime.fromisoformat(updated_date)
        creator = event['creator']['email']
        if 'dateTime' in event['start']:
            allDay = False
            start = datetime.datetime.fromisoformat(event['start']['dateTime']).strftime("%Y/%m/%d %H:%M:%S.%f")
            end = datetime.datetime.fromisoformat(event['end']['dateTime']).strftime("%Y/%m/%d %H:%M:%S.%f")
            date = None
        else:
            allDay = True
            start = None
            end = None
            date = event['start']['date']
        event_data.append(str(created))
        event_data.append(str(updated))
        event_data.append(creator)
        event_data.append(allDay)
        if allDay:
            event_data.append(start)
            event_data.append(end)
            event_data.append(str(date))
        else:
            event_data.append(str(start))
            event_data.append(str(end))
            event_data.append(date)
        events_data.append(event_data)

    for insert_data in events_data:
        try:
            data = Calendar.check_schedule_event_id(insert_data[0])[0]
        except Exception:
            result = {}
            user_id = User.check_user_mail(insert_data[7])[0]
            Calendar.insert_schedule(user_id, insert_data)
            result['user_id'] = user_id
            result['data'] = insert_data
            results.append(result)

    response = {
        'status': 200,
        'data': results
    }

    return response
