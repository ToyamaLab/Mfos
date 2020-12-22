import json
from flask import Blueprint, request
import datetime
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from flaskr.api.v1.account_management import google_account_management
from flaskr.database import connect_db
from flaskr.api.v1.member import (
    User,
    Information,
)

api_v1_member_bp = Blueprint('apiv1_member', __name__, url_prefix='/api/v1/member')
SCOPES_SPREADSHEETS = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
SEARCH_SHEET_ID = '16a8Xq-lL6VVIQ_WToQZIntFfa3b5tmOIB91cY75N-YY'
google_credentials = google_account_management(SCOPES_SPREADSHEETS)



def initialize_spreadSheets():
    credentials = google_credentials
    return build('sheets', 'v4', credentials=credentials)


@api_v1_member_bp.route('/member/regist', methods=['POST'])
def regist_member_information():
    raw_data = request.get_data()
    information_data = json.loads(raw_data.decode(encoding='utf-8'))
    db_conn = connect_db()
    db_cur = db_conn.cursor()

    user_id = User.check_user_mail(information_data['mail'])['user_id']
    response = Information.insert_information(user_id, information_data)

    db_cur.close()
    db_conn.commit()
    db_conn.close()

    return response


@api_v1_member_bp.route('/member/update', methods=['POST'])
def update_member_information():
    raw_data = request.get_data()
    information_data = json.loads(raw_data.decode(encoding='utf-8'))
    db_conn = connect_db()
    db_cur = db_conn.cursor()

    user_id = User.check_user_mail(information_data['mail'])['user_id']
    response = Information.update_information(user_id, information_data)

    db_cur.close()
    db_conn.commit()
    db_conn.close()

    return response


@api_v1_member_bp.route('/sheet/member', methods=['GET'])
def update_information_spreadsheet():
    sheet = initialize_spreadSheets()
    search_query = sheet.spreadsheets().values().get(spreadsheetId=SEARCH_SHEET_ID, range="社員情報!A2:E2500").execute()
    targets = search_query['values']
    result = []

    for i in range(len(targets)):
        try:
            user_id = User.check_user_mail(targets[i][1])[0]
            print(user_id)
        except Exception:
            print('insert gmail')
            User.insert_gmail(targets[i][1])
            result.append(targets[i][1])

    response = {
        'status': 200,
        'data': result
    }

    return response


@api_v1_member_bp.route('/sheet/information', methods=['GET'])
def regist_member_spreadsheet():
    sheet = initialize_spreadSheets()
    search_query = sheet.spreadsheets().values().get(spreadsheetId=SEARCH_SHEET_ID, range="社員情報!A2:E2500").execute()
    targets = search_query['values']
    result = []
    try:
        for i in range(len(targets)):
            print(i)
            information_data = {}
            information_data['name'] = targets[i][0]
            information_data['mail'] = targets[i][1]
            information_data['department'] = targets[i][2]
            information_data['sex'] = targets[i][4]
            information_data['birthday'] = targets[i][3]
            print(information_data)
            user_id = User.check_user_mail(information_data['mail'])[0]
            print("kazukazu")
            information_id = Information.check_information_mail(user_id)
            print(information_data)
            if information_id is None:
                print("answer")
                Information.insert_information(user_id, information_data)
            else:
                Information.update_information(user_id, information_data)
            result.append(information_data)

        response = {
            'status': 200,
            'data': result
        }

    except Exception as e:
        response = {
            'Error': e,
            'Hint': "Perhaps the member registration method should be done first."
        }

    return response
