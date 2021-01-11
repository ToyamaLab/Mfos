import json
from flask import Blueprint, request
from googleapiclient.discovery import build
from flaskr.api.v1.account_management import google_account_management
from flaskr.api.v1.member import (
    User,
    Information,
)

api_v1_member_bp = Blueprint('apiv1_member', __name__, url_prefix='/api/v1/member')
SCOPES_SPREADSHEETS = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
SEARCH_SHEET_ID = '16a8Xq-lL6VVIQ_WToQZIntFfa3b5tmOIB91cY75N-YY'
google_credentials = google_account_management(SCOPES_SPREADSHEETS)


def initialize_spreadSheets():
    """
    作成者: kazu
    概要: googleの認証を行い,　APIを使用可能にするメソッド
    """
    credentials = google_credentials
    return build('sheets', 'v4', credentials=credentials, cache_discovery=False)


@api_v1_member_bp.route('/regist', methods=['POST'])
def regist_member_information():
    """
    作成者: kazu
    概要: 従業員情報をHTTPリクエストによって登録するためのメソッド
    """
    raw_data = request.get_data()
    information_data = json.loads(raw_data.decode(encoding='utf-8'))
    response = {}

    try:
        new_user_data = {}
        new_user_data['gmail'] = information_data['gmail']
        if 'slack_id' in information_data:
            new_user_data['slack_id'] = information_data['slack_id']
        else:
            new_user_data['slack_id'] = None
        new_information_data = {}
        new_information_data['name'] = information_data['name']
        new_information_data['department'] = information_data['department']
        new_information_data['sex'] = information_data['sex']
        new_information_data['birthday'] = information_data['birthday']
    except Exception:
        response = {
            'status': 'Error',
            'error': 'The request data is invalid'
        }
        return response

    user_id_data = User.check_user_mail(information_data['gmail'])
    if not user_id_data:
        try:
            User.insert_user(new_user_data)
            response['user_data'] = new_user_data
        except Exception:
            response = {
                'status': 'Error',
                'error': 'The request data is invalid [users]'
            }
            return response

        try:
            user_id = User.check_user_mail(information_data['gmail'])[0]
            Information.insert_information(user_id, new_information_data)
            response['information_data'] = new_information_data
        except Exception:
            user_id = User.check_user_mail(information_data['gmail'])[0]
            User.delete_by_id(user_id)
            response = {
                'status': 'Error',
                'error': 'The request data is invalid [information]'
            }

    else:
        user_id = User.check_user_mail(information_data['gmail'])[0]
        information_id = Information.check_information_mail(user_id)
        if information_id is None:
            Information.insert_information(user_id, new_information_data)
            response['user_data'] = new_user_data
            response['information_data'] = new_information_data
        else:
            response = {
                'status': 'Error',
                'error': 'The mail address is already registered',
                'user_id': user_id
            }

    return response


@api_v1_member_bp.route('/update', methods=['POST'])
def update_member_information():
    """
        作成者: kazu
        概要: 従業員情報をHTTPリクエストによって更新するためのメソッド
    """
    raw_data = request.get_data()
    information_data = json.loads(raw_data.decode(encoding='utf-8'))
    response = information_data

    try:
        user_id = User.check_user_mail(information_data['gmail'])[0]
    except Exception:
        response = {
            'status': 'Error',
            'error': 'The mail address is not registered',
        }
        return response

    information_id = Information.check_information_mail(user_id)
    if information_id is None:
        try:
            new_information_data = {}
            new_information_data['name'] = information_data['name']
            new_information_data['department'] = information_data['department']
            new_information_data['sex'] = information_data['sex']
            new_information_data['birthday'] = information_data['birthday']
        except Exception:
            response = {
                'status': 'Error',
                'error': 'The request data is invalid'
            }
            return response
        User.update_user(user_id, information_data)
        Information.insert_information(user_id, new_information_data)
    else:
        User.update_user(user_id, information_data)
        Information.update_information(user_id, information_data)

    return response


@api_v1_member_bp.route('/sheet/information', methods=['POST'])
def regist_information_spreadsheet():
    """
            作成者: kazu
            概要: 従業員情報をGoogle Spread Sheetより抜き出し登録するメソッド
    """
    sheet = initialize_spreadSheets()
    search_query = sheet.spreadsheets().values().get(spreadsheetId=SEARCH_SHEET_ID, range="社員情報!A2:E2500").execute()
    targets = search_query['values']
    results = []
    errors = []

    for i in range(len(targets)):
        try:
            user_data = {}
            user_data['gmail'] = targets[i][1]
            information_data = {}
            information_data['name'] = targets[i][0]
            information_data['mail'] = targets[i][1]
            information_data['department'] = targets[i][2]
            information_data['sex'] = targets[i][4]
            information_data['birthday'] = targets[i][3]
        except Exception:
            errors.append(targets[i][1])
            continue

        user_id_data = User.check_user_mail(targets[i][1])

        if not user_id_data:
            User.insert_gmail(user_data['gmail'])
            user_id = User.check_user_mail(user_data['gmail'])[0]
            Information.insert_information(user_id, information_data)
        else:
            user_id = User.check_user_mail(user_data['gmail'])[0]
            information_id = Information.check_information_mail(user_id)
            if information_id is None:
                Information.insert_information(user_id, information_data)
            else:
                Information.update_information(user_id, information_data)

        result_data = {}
        result_data['user_id'] = user_id
        result_data['information_data'] = information_data
        results.append(result_data)

    response = {
        'error_data': errors,
        'success_data': results
    }

    return response
