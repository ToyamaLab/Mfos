import json
import os
import mysql.connector as mydb
from datetime import datetime
from flask import Blueprint, request, abort, jsonify
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from flaskr.database import connect_db
from flaskr.database import db
from flaskr.api.v1.member.models import Information

api_v1_member_bp = Blueprint('apiv1_member', __name__, url_prefix='/api/v1/member')
KEY_FILE_LOCATION = 'credentials.json'
SCOPES_SPREADSHEETS = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
SEARCH_SHEET_ID = '16a8Xq-lL6VVIQ_WToQZIntFfa3b5tmOIB91cY75N-YY'


def initialize_spreadSheets():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_LOCATION, SCOPES_SPREADSHEETS)
    return build('sheets', 'v4', credentials=credentials)


@api_v1_member_bp.route('/member/regist', methods=['POST'])
def regist_member_information():
    raw_data = request.get_data()
    message_data = json.loads(raw_data.decode(encoding='utf-8'))
    db_conn = connect_db()
    db_cur = db_conn.cursor()

    try:
        db_cur.execute("INSERT INTO messages(department, sex, age, created_at, updated_at) VALUES(%s, %s, %s, %s, %s)",
                       (message_data['department'], message_data['sex'], message_data['age'], datetime.now(),
                        datetime.now()))
        response = raw_data
    except KeyError:
        response = raw_data

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

    try:
        if 'department' in information_data:
            department = information_data['department']
        if 'sex' in information_data:
            sex = information_data['sex']
        if 'age' in information_data:
            age = information_data['age']

        db_cur.execute("INSERT INTO messages(department, sex, updated_at) VALUES(%s, %s, %s)",
                       (message_data['department'], message_data['sex'], datetime.now()))
        response = raw_data
    except KeyError:
        response = raw_data

    db_cur.close()
    db_conn.commit()
    db_conn.close()

    return response


@api_v1_member_bp.route('/sheet', methods=['GET'])
def update_member_spreadsheet():
    sheet = initialize_spreadSheets()
    search_query = sheet.spreadsheets().values().get(spreadsheetId=SEARCH_SHEET_ID, range="社員情報!A2:D2500").execute()
    targets = search_query['values']
    db_conn = connect_db()
    db_cur = db_conn.cursor()
    response = 'ok'

    for i in range(len(targets)):
        try:
            db_cur.execute(
                "INSERT INTO information(department, sex, age, created_at, update_at) VALUES(%s, %s, %s, %s, %s)",
                (targets[i][1], targets[i][3], targets[i][2], datetime.now(), datetime.now()))
        except KeyError:
            response = 'error'

    db_cur.close()
    db_conn.commit()
    db_conn.close()

    return response
