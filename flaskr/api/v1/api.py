from flask import Blueprint
from .member import api as member
from .calendar import api as calendar
from .gmail import api as gmail
from .zoom import  api as zoom

api_v1_main_bp = Blueprint('apiv1_main', __name__, url_prefix='/api/v1')

@api_v1_main_bp.route('/run', methods=['POST'])
def run_all_api():
    """
        作成者: kazu
        概要: 各Webアプリケーションから情報を取得, 保存する関数. heroku schedulerで定期実行する.
    """
    member_result = member.regist_information_spreadsheet()
    calendar_result = calendar.regist_calendar()
    # gmail_result = gmail.regist_gmail()
    zoom_result = zoom.regist_meetings()
    return {
        'status': 200,
        'member': member_result,
        'calendar': calendar_result,
        'gmail': gmail_result,
        'zoom': zoom_result
    }
