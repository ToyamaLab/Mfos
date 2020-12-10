import datetime
from flask import Blueprint
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from flaskr.database import connect_db
from datetime import datetime as dt
from flaskr.api.v1.calendar.models import Calendar

api_v1_calendar_bp = Blueprint('apiv1_calendar', __name__, url_prefix='/api/v1/calendar')
KEY_FILE_LOCATION = 'credentials.json'
GOOGLE_CALENDAR_ID = 'kazu.agestock@gmail.com'
GOOGLE_CALENDAR_SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def initialize_calendar():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, GOOGLE_CALENDAR_SCOPES)
    return build('calendar', 'v3', credentials=credentials)


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

    db_conn = connect_db()
    db_cur = db_conn.cursor()

    for insert_data in events_data:
        db_cur.execute("INSERT INTO schedule(event_id, link, title, description, location, event_created, event_updated, creator, all_day, start, end, date, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        (insert_data[0], insert_data[1], insert_data[2], insert_data[3], insert_data[4], insert_data[5], insert_data[6], insert_data[7], insert_data[8], insert_data[9], insert_data[10], insert_data[11], dt.now(), dt.now()))

    response = {
        'status': 200
    }

    db_cur.close()
    db_conn.commit()
    db_conn.close()

    return response
