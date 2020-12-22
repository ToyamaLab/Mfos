import os
import json
from oauth2client.service_account import ServiceAccountCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

KEY_FILE_LOCATION = 'credentials.json'
KEY_FILE_LOCATION2 = 'credentials_gmail.json'

def zoom_account_management():
    zoom_user_id = os.getenv('ZOOM_USER_ID')
    zoom_client_id = os.getenv('ZOOM_CLIENT_ID')
    zoom_client_secret = os.getenv('ZOOM_CLIENT_SECRET')

    if (zoom_user_id or zoom_client_id or zoom_client_secret) is None:
        import account
        zoom_user_id = account.userId
        zoom_client_id = account.client_id
        zoom_client_secret = account.client_secret

    accounts = {
        'zoom_user_id': zoom_user_id,
        'zoom_client_id': zoom_client_id,
        'zoom_client_secret': zoom_client_secret
    }
    return accounts


def google_account_management(scope):
    try:
        google_key = json.loads(os.getenv('GOOGLE_KEYFILE'))
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(google_key, scope)
    except Exception:
        credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, scope)

    return credentials


def gmail_account_management(scope):
    try:
        gmail_key = json.loads(os.getenv('GMAIL_KEYFILE'))
        flow = InstalledAppFlow.from_client_config(gmail_key, scope)
    except Exception:
        flow = InstalledAppFlow.from_client_secrets_file(KEY_FILE_LOCATION2, scope)

    credentials = flow.run_console()

    return credentials
