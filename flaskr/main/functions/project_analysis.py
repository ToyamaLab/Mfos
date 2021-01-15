import numpy as np
from flaskr.database import db
from flaskr.main.models import (
    User,
    Information,
    Mail,
    Calendar,
    SlackChannelMember,
    SlackChannel,
    SlackMessage,
    ZoomMeeting,
    Importance
)


def search_word(target, query):
    if query in target:
        return True
    else:
        return False


def analytics(project_name):
    """
        作成者: kazu
        概要: 各ユーザーのプロジェクト貢献度を計算する元となるデータを取得・処理する
    """
    users = db.session.query(User, Information).join(Information, User.id == Information.user_id).with_entities(
        User.id, User.gmail, User.slack_id, Information.name, Information.department).all()
    user_data = {}
    user_id = []
    user_data['user_count'] = len(users)
    for user in users:
        user_id.append(user[0])
        user_data[user[0]] = {}
        user_data[user[0]]['gmail'] = user[1]
        user_data[user[0]]['slack_id'] = user[2]
        user_data[user[0]]['name'] = user[3]
        user_data[user[0]]['department'] = user[4]

        # MAIL周り
        try:
            mail_data = Mail.select_mail(user[0])
            project_mail_count = 0
            for m in mail_data:
                if search_word(m['subject'], "【" + project_name + "】"):
                    project_mail_count += 1
            user_data[user[0]]['mail_count'] = project_mail_count
        except AttributeError:
            user_data[user[0]]['mail_count'] = 0


        # Calendar周り
        try:
            calendar_data = Calendar.select_schedule_id(user[0])
            project_schedule_count = 0
            for c in calendar_data:
                if search_word(c['title'], "【" + project_name + "】"):
                    project_schedule_count += 1
            user_data[user[0]]['schedule_count'] = project_schedule_count
        except AttributeError:
            user_data[user[0]]['schedule_count'] = 0


        # Slack周り
        try:
            slack_data = db.session.query(SlackMessage, SlackChannel).join(SlackChannel, SlackMessage.channel_id == SlackChannel.id).with_entities(
                SlackMessage.id, SlackMessage.event_id, SlackMessage.event_type, SlackMessage.event_time, SlackMessage.message_time, SlackMessage.file_id, SlackMessage.text, SlackMessage.reaction, SlackChannel.name
            ).filter(SlackMessage.user_id==user[0]).all()
            project_slack_message_count = 0
            for s in slack_data:
                if s[2] == "message":
                    if search_word(s[6], "【" + project_name + "】"):
                        project_slack_message_count += 1
            user_data[user[0]]['slack_count'] = project_slack_message_count
        except AttributeError:
            user_data[user[0]]['slack_count'] = 0

        # Zoom周り
        try:
            zoom_data = ZoomMeeting.select_meeting(user[0])
            project_zoom_meeting_count = 0
            for z in zoom_data:
                if search_word(z[1], "【" + project_name + "】"):
                    project_zoom_meeting_count += 1
            user_data[user[0]]['zoom_count'] = project_zoom_meeting_count
        except AttributeError:
            user_data[user[0]]['zoom_count'] = 0

    user_data['user_id'] = user_id

    return user_data



def project_contribution(project_id, analysis):
    """
        作成者: kazu
        概要: 各ユーザーのデータと, プロジェクトごとに設定されている重要度から各プロジェクトの貢献ランクを提示する関数
    """
    rank_data = []
    importance = Importance.select_importance(project_id)
    total_importance = importance['mail'] + importance['schedule'] + importance['slack'] + importance['zoom']
    for i in analysis['user_id']:
        analysis[i]['contribution_result'] = (importance['mail']/total_importance)*(float(analysis[i]['contribution_mail'])/100) + (importance['schedule'] / total_importance) * (float(analysis[i]['contribution_schedule']) / 100) + (importance['slack']/total_importance)*(float(analysis[i]['contribution_slack'])/100) + (importance['zoom']/total_importance)*(float(analysis[i]['contribution_zoom'])/100)
        rank_data.append(analysis[i]['contribution_result'])

    q25, q50, q75 = np.percentile(rank_data, [25, 50, 75])

    for i in analysis['user_id']:
        if analysis[i]['contribution_result'] == 0:
            analysis[i]['contribution_rank'] = "Z"
        elif analysis[i]['contribution_result'] < q25:
            analysis[i]['contribution_rank'] = "D"
        elif analysis[i]['contribution_result'] < q50:
            analysis[i]['contribution_rank'] = "C"
        elif analysis[i]['contribution_result'] < q75:
            analysis[i]['contribution_rank'] = "B"
        else:
            analysis[i]['contribution_rank'] = "A"

    return analysis


