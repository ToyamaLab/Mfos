import json
import re
import os
import mysql.connector as mydb
import pymysql
import time
from flask import Blueprint, render_template, request
from flaskr.database import db
from flaskr.main.functions import project_analysis
from datetime import datetime
from flaskr.database import connect_db
from flaskr.main.models import (
    User,
    Information,
    Mail,
    Calendar,
    SlackChannelMember,
    SlackChannel,
    SlackMessage,
    ZoomMeeting,
    Project,
    Importance
)

main_bp = Blueprint('main', __name__, template_folder='templates')


@main_bp.route('/')
def top_menu():
    """
        作成者: kazu
        概要: トップ画面
    """
    user_data = None
    while not user_data:
        print("while")
        try:
            users_data = db.session.query(User, Information).join(Information, User.id == Information.user_id).with_entities(
                User.id, User.gmail, User.slack_id, Information.name, Information.department).all()
            db.session.commit()
            db.session.close()
            break
        except Exception:
            print('リロード')
            time.sleep(5)
            continue

    users = []
    for user_data in users_data:
        user = {}
        user['id'] = user_data[0]
        user['mail'] = user_data[1]
        user['slack_id'] = user_data[2]
        user['name'] = user_data[3]
        user['department'] = user_data[4]
        users.append(user)

    projects = Project.select_project()

    return render_template(
        'main/top.html',
        users=users,
        projects=projects
    )


@main_bp.route('/user')
def user_detail():
    """
        作成者: kazu
        概要: 従業員情報を表示する画面
    """
    user_id = request.args.get('id')
    status = 0
    while status == 0:
        try:
            user = User.select_users_by_id(user_id)
            information = Information.select_information(user_id)
            mail = Mail.select_mail(user_id)
            schedule = Calendar.select_schedule_id(user_id)
            slack_channel = db.session.query(SlackChannelMember, SlackChannel).join(SlackChannel, SlackChannelMember.channel_id == SlackChannel.id).with_entities(
                SlackChannelMember.user_id, SlackChannelMember.channel_id, SlackChannel.name).filter(SlackChannelMember.user_id==user_id).all()
            print(slack_channel)
            db.session.commit()
            db.session.close()
            slack_message = db.session.query(SlackMessage, SlackChannel).join(SlackChannel, SlackMessage.channel_id == SlackChannel.id).with_entities(
                SlackMessage.id, SlackMessage.event_id, SlackMessage.event_type, SlackMessage.event_time, SlackMessage.message_time, SlackMessage.file_id, SlackMessage.text, SlackMessage.reaction, SlackChannel.name).filter(SlackMessage.user_id==user_id).all()
            db.session.commit()
            db.session.close()
            zoom_meeting = ZoomMeeting.select_meeting(user_id)
            status = 1
        except Exception:
            time.sleep(5)
            continue


    return render_template(
        'main/user_detail.html',
        user=user,
        information=information,
        mail=mail,
        schedule=schedule,
        slack_channel=slack_channel,
        slack_message=slack_message,
        zoom_meeting=zoom_meeting,
    )

@main_bp.route('/project')
def project_detail():
    """
        作成者: kazu
        概要: 各プロジェクト毎の情報を表示する画面
    """
    project_name = request.args.get('name')
    return project_detail_load(project_name)


def project_detail_load(project_name):
    """
        作成者: kazu
        概要: 各プロジェクト毎の情報を表示する関数
    """
    status = 0
    while status == 0:
        try:
            analysis = project_analysis.analytics(project_name)
            status = 1
        except Exception:
            time.sleep(5)
            continue

    names = []
    names_str = ""
    gmail_data = []
    schedule_data = []

    total_mail_count = 0
    total_schedule_count = 0
    total_slack_count = 0
    total_zoom_count = 0

    for i in analysis['user_id']:
        information = Information.select_information(i)
        names_updated = []
        names.append(information['name'])
        gmail_data.append(analysis[i]['mail_count'])
        schedule_data.append(analysis[i]['schedule_count'])
        total_mail_count += analysis[i]['mail_count']
        total_schedule_count += analysis[i]['schedule_count']
        total_slack_count += analysis[i]['slack_count']
        total_zoom_count += analysis[i]['zoom_count']

    for i in analysis['user_id']:
        analysis[i]['contribution_mail'] = 0
        analysis[i]['contribution_schedule'] = 0
        analysis[i]['contribution_slack'] = 0
        analysis[i]['contribution_zoom'] = 0
        if total_mail_count != 0:
            analysis[i]['contribution_mail'] = '{:.1f}'.format((analysis[i]['mail_count']/total_mail_count)*100)
        if total_schedule_count != 0:
            analysis[i]['contribution_schedule'] = '{:.1f}'.format((analysis[i]['schedule_count'] / total_schedule_count) * 100)
        if total_slack_count != 0:
            analysis[i]['contribution_slack'] = '{:.1f}'.format((analysis[i]['slack_count'] / total_slack_count) * 100)
        if total_zoom_count != 0:
            analysis[i]['contribution_zoom'] = '{:.1f}'.format((analysis[i]['zoom_count'] / total_zoom_count) * 100)

    project_id = Project.select_project_by_name(project_name)[0]
    importance = Importance.select_importance(project_id)
    analysis = project_analysis.project_contribution(project_id, analysis)

    data = {}
    data['names'] = names
    data['gmail_data'] = gmail_data
    data['schedule_data'] = schedule_data

    names_str = str(names)[1:-1].replace("'", "")

    return render_template(
        'main/project_detail.html',
        project_name=project_name,
        analysis=analysis,
        data=data,
        names_str=names_str,
        importance=importance
    )


@main_bp.route('/project', methods=['POST'])
def project_importance_update():
    """
        作成者: kazu
        概要: 各プロジェクト毎に設定する各ウェブアプリケーションの重要度をフォームから更新する関数
    """
    project_name = request.args.get('name')
    values = {
        'project_id': Project.select_project_by_name(project_name)[0],
        'importance': {
            'mail': request.form.get('mail'),
            'schedule': request.form.get('schedule'),
            'slack': request.form.get('slack'),
            'zoom': request.form.get('zoom')
        }
    }
    Importance.update_importance(values)
    return project_detail_load(project_name)




