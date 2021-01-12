from sqlalchemy import func, CheckConstraint, UniqueConstraint
from flaskr.database import db
from datetime import datetime


class User(db.Model):
    """
    作成者: kazu
    概要: 従業員識別情報を保存しているテーブル
    """
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True)  # 主キー
    slack_id = db.Column(db.String(20), index=True, unique=True)
    gmail = db.Column(db.String(50), index=True, unique=True)
    created_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime)
    mail = db.relationship('Mail', backref='user', lazy=True)
    information = db.relationship('Information', backref='user', lazy=True)
    calendar = db.relationship('Calendar', backref='user', lazy=True)
    slack_channel_member = db.relationship('SlackChannelMember', backref='user', lazy=True)
    slack_message = db.relationship('SlackMessage', backref='user', lazy=True)
    zoom_access_token = db.relationship('ZoomAccessToken', backref='user', lazy=True)
    zoom_meeting = db.relationship('ZoomMeeting', backref='user', lazy=True)
    zoom_participant = db.relationship('ZoomParticipant', backref='user', lazy=True)

    def __init__(self, slack_id, gmail, created_at, updated_at):
        self.slack_id = slack_id
        self.gmail = gmail
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, slack_id={self.slack_id}, gmail={self.gmail}, created_at={self.created_at}, updated_at={self.updated_at}"

    @classmethod
    def select_users(cls):
        raw_data = db.session.query(cls).with_entities(cls.id, cls.slack_id, cls.gmail).all()
        data = {}
        data['id'] = raw_data[0]
        data['slack_id'] = raw_data[1]
        data['gmail'] = raw_data[2]
        return data

    @classmethod
    def select_users_by_id(cls, user_id):
        return db.session.query(cls).with_entities(cls.id, cls.slack_id, cls.gmail).filter(cls.id == user_id).first()

    @classmethod
    def insert_user(self, data):
        target = User(gmail=data['gmail'], slack_id=data['slack_id'], created_at=datetime.now(),
                      updated_at=datetime.now())
        db.session.add(target)
        db.session.commit()

    @classmethod
    def insert_gmail(self, gmail):
        target = User(gmail=gmail, slack_id=None, created_at=datetime.now(), updated_at=datetime.now())
        db.session.add(target)
        db.session.commit()

    @classmethod
    def update_user(cls, user_id, information_data):
        user = db.session.query(cls).filter(cls.id == user_id).first()
        if 'gmail' in information_data:
            user.gmail = information_data['gmail']
        if 'slack_id' in information_data:
            user.slack_id = information_data['slack_id']
        user.updated_at = datetime.now()
        db.session.commit()

    @classmethod
    def check_user_mail(cls, gmail):
        return db.session.query(cls).with_entities(cls.id).filter(cls.gmail == gmail).first()

    @classmethod
    def check_user_slack_id(cls, slack_id):
        return db.session.query(cls).with_entities(cls.id).filter(cls.slack_id == slack_id).first()

    @classmethod
    def delete_by_id(cls, user_id):
        db.session.query(cls).filter(cls.id == user_id).delete()
        db.session.commit()


class Project(db.Model):
    __tablename__ = 'projects'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    name = db.Column(db.String(50), index=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, name, created_at, updated_at):
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, name = {self.name}, create_at={self.created_at}, update_at={self.updated_at} "

    @classmethod
    def select_project(cls):
        raw_data = db.session.query(cls).with_entities(cls.id, cls.name).all()
        result_data = []
        for r in raw_data:
            data = {}
            data['id'] = r[0]
            data['name'] = r[1]
            result_data.append(data)
        return result_data


class Information(db.Model):
    """
        作成者: kazu
        概要: 従業員情報を保存しているテーブル
    """
    __tablename__ = 'information'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(20), index=True)
    department = db.Column(db.String(30), index=True)
    birthday = db.Column(db.DateTime)
    sex = db.Column(db.String(5))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, user_id, name, department, birthday, sex, created_at, updated_at):
        self.user_id = user_id
        self.name = name
        self.department = department
        self.birthday = birthday
        self.sex = sex
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, user_id = {self.user_id}, name = {self.name}, department = {self.department}, birthday = {self.birthday}, sex = {self.sex}, create_at={self.created_at}, update_at={self.updated_at} "

    @classmethod
    def select_information(cls, user_id):
        raw_data = cls.query.with_entities(
            cls.id, cls.user_id, cls.name, cls.department, cls.birthday, cls.sex
        ).filter(cls.user_id == user_id).first()
        data = {}
        data['id'] = raw_data[0]
        data['user_id'] = raw_data[1]
        data['name'] = raw_data[2]
        data['department'] = raw_data[3]
        data['birthday'] = raw_data[4].date()
        data['sex'] = raw_data[5]
        return data

    @classmethod
    def insert_information(self, user_id, information_data):
        target = Information(user_id=user_id, name=information_data['name'], department=information_data['department'],
                             birthday=information_data['birthday'], sex=information_data['sex'],
                             created_at=datetime.now(), updated_at=datetime.now())
        db.session.add(target)
        db.session.commit()

    @classmethod
    def update_information(cls, user_id, information_data):
        information = db.session.query(cls).filter(cls.user_id == user_id).first()
        if 'name' in information_data:
            information.name = information_data['name']
        if 'department' in information_data:
            information.department = information_data['department']
        if 'sex' in information_data:
            information.sex = information_data['sex']
        if 'birthday' in information_data:
            information.birthday = information_data['birthday']
        information.updated_at = datetime.now()
        db.session.commit()

    @classmethod
    def check_information_mail(cls, user_id):
        return db.session.query(cls).with_entities(cls.id).filter(cls.user_id == user_id).first()


# gmail APIで取得したメール情報を格納したテーブル
class Mail(db.Model):
    __tablename__ = 'gmail'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message_id = db.Column(db.String(50), nullable=False, unique=True)
    sender_name = db.Column(db.String(50), nullable=False)
    sender_email = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    subject = db.Column(db.String(100))
    message = db.Column(db.String(2000))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, user_id, message_id, sender_name, sender_email, date, subject, message, created_at, updated_at):
        self.user_id = user_id
        self.message_id = message_id
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.date = date
        self.subject = subject
        self.message = message
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, user_id = {self.user_id}, message_id = {self.message_id}, sender_name = {self.sender_name}, sender_email = {self.sender_email}, date = {self.date}, subject = {self.subject}, message = {self.message}, create_at={self.created_at}, update_at={self.updated_at} "

    @classmethod
    def select_mail(cls, user_id):
        raw_data = cls.query.with_entities(
            cls.id, cls.user_id, cls.message_id, cls.sender_name, cls.sender_email, cls.date, cls.subject, cls.message
        ).filter(cls.user_id == user_id).order_by(cls.date.asc(), cls.id.asc()).all()
        result_data = []
        for r in raw_data:
            data = {}
            data['id'] = r[0]
            data['user_id'] = r[1]
            data['message_id'] = r[2]
            data['sender_name'] = r[3]
            data['sender_email'] = r[4]
            data['date'] = r[5]
            data['subject'] = r[6]
            data['message'] = r[7]
            result_data.append(data)
        return result_data

    @classmethod
    def insert_message(self):
        print(self.created_at)
        db.session.add(self)

    @classmethod
    def insert_mail(self, user_id, message, sender_name, sender_email, date):
        target = Mail(user_id=user_id, message_id=message['ID'], sender_name=sender_name, sender_email=sender_email,
                      date=date, subject=message['Subject'], message=None, created_at=datetime.now(),
                      updated_at=datetime.now())
        db.session.add(target)
        db.session.commit()
        # db_cur.execute(
        #     "INSERT INTO gmail(user_id, message_id, sender_name, sender_email, date, message,  created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
        #     (user_id, message['ID'], sender_name, sender_email, date, message['Subject'], datetime.now(), datetime.now()))


# Google Calendar APIで取得したカレンダー情報を格納したテーブル
class Calendar(db.Model):
    __tablename__ = 'schedule'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.String(50), nullable=False, unique=True)
    link = db.Column(db.String(200), nullable=False)
    event_created = db.Column(db.DateTime, nullable=False)
    event_updated = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(400))
    location = db.Column(db.String(50))
    creator = db.Column(db.String(50), nullable=False)
    all_day = db.Column(db.Boolean, nullable=False, default=False)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    date = db.Column(db.DateTime)
    sort_date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, user_id, event_id, link, event_created, event_updated, title, description, location, creator,
                 all_day, start, end, date, sort_date, created_at, updated_at):
        self.user_id = user_id
        self.event_id = event_id
        self.link = link
        self.event_created = event_created
        self.event_updated = event_updated
        self.title = title
        self.description = description
        self.location = location
        self.creator = creator
        self.all_day = all_day
        self.start = start
        self.end = end
        self.date = date
        self.sort_date = sort_date
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, user_id = {self.user_id}, event_id = {self.event_id}, link = {self.link}, event_created = {self.event_created}, event_updated = {self.event_updated}, title = {self.title}, description = {self.description}, location = {self.location}, creator = {self.creator}, all_day = {self.all_day}, start = {self.start}, end = {self.end}, date = {self.date}, sort_date = {self.sort_date}, create_at={self.created_at}, update_at={self.updated_at} "

    @classmethod
    def insert_message(self):
        print(self.created_at)
        db.session.add(self)

    @classmethod
    def insert_schedule(cls, user_id, insert_data):
        if insert_data[8] == 0:
            sote_date = insert_data[9]
        elif insert_data[8] == 1:
            sote_date = insert_data[11]
        target = Calendar(user_id=user_id, event_id=insert_data[0], link=insert_data[1], title=insert_data[2],
                          description=insert_data[3], location=insert_data[4], event_created=insert_data[5],
                          event_updated=insert_data[6], creator=insert_data[7], all_day=insert_data[8],
                          start=insert_data[9], end=insert_data[10], date=insert_data[11], sort_date=sote_date,
                          created_at=datetime.now(), updated_at=datetime.now())
        db.session.add(target)
        db.session.commit()
        # db_cur.execute(
        #     "INSERT INTO schedule(user_id, event_id, link, title, description, location, event_created, event_updated, creator, all_day, start, end, date, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        #     (user_id, insert_data[0], insert_data[1], insert_data[2], insert_data[3], insert_data[4], insert_data[5],
        #      insert_data[6], insert_data[7], insert_data[8], insert_data[9], insert_data[10], insert_data[11], datetime.now(),
        #      datetime.now()))

    @classmethod
    def check_schedule_event_id(cls, event_id):
        return db.session.query(cls).with_entities(cls.id).filter(cls.event_id == event_id).first()

    @classmethod
    def select_schedule_id(cls, user_id):
        raw_data = db.session.query(cls).with_entities(
            cls.id, cls.user_id, cls.event_id, cls.link, cls.event_created, cls.event_updated, cls.title,
            cls.description, cls.location, cls.creator, cls.all_day, cls.start, cls.end, cls.date
        ).filter(cls.user_id == user_id).order_by(cls.sort_date.asc(), cls.all_day.asc()).all()
        result_data = []
        for r in raw_data:
            data = {}
            data['id'] = r[0]
            data['user_id'] = r[1]
            data['event_id'] = r[2]
            data['link'] = r[3]
            data['event_created'] = r[4]
            data['event_updated'] = r[5]
            data['title'] = r[6]
            data['description'] = r[7]
            data['location'] = r[8]
            data['creator'] = r[9]
            if r[10] == 0:
                data['date'] = str(r[11]) + " - " + str(r[12])
            elif r[10] == 1:
                data['date'] = r[13].date()
            result_data.append(data)
        return result_data


class SlackChannel(db.Model):
    """
        作成者: kazu
        概要: Slack内のチャネル情報を保存するテーブル
    """
    __tablename__ = 'slack_channels'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    channel_id = db.Column(db.String(50), index=True, nullable=False)
    name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    channel = db.relationship('SlackMessage', backref='channel', lazy=True)
    member = db.relationship('SlackChannelMember', backref='channel', lazy=True)

    def __init__(self, channel_id, name, created_at, updated_at):
        self.channel_id = channel_id
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, channel_id = {self.channel_id}, name = {self.id}, created_at = {self.created_at}, updated_at = {self.updated_at}"

    @classmethod
    def select_channel_id(cls, channel_id):
        return db.session.query(cls).with_entities(cls.id).filter(cls.channel_id == channel_id).first()

    @classmethod
    def insert_channel(cls, channel_id, name):
        target = SlackChannel(channel_id=channel_id, name=name, created_at=datetime.now(), updated_at=datetime.now())
        db.session.add(target)
        db.session.commit()

    @classmethod
    def update_channel_name(cls, channel_id, name):
        channel = db.session.query(cls).filter(cls.channel_id == channel_id).first()
        channel.name = name
        channel.updated_at = datetime.now()
        db.session.commit()
        return channel


class SlackChannelMember(db.Model):
    """
            作成者: kazu
            概要: チャネルとメンバーの関係を保存するテーブル
    """
    __tablename__ = 'slack_channel_members'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('slack_channels.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, user_id, channel_id, created_at, updated_at):
        self.user_id = user_id
        self.channel_id = channel_id
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, user_id = {self.user_id}, channel_id = {self.channel_id}, created_at = {self.created_at}, updated_at = {self.updated_at}"

    @classmethod
    def insert_channel_member(cls, user_id, channel_id):
        target = SlackChannelMember(user_id=user_id, channel_id=channel_id, created_at=datetime.now(),
                                    updated_at=datetime.now())
        db.session.add(target)
        db.session.commit()
        return target

    @classmethod
    def check_by_ids(cls, user_id, channel_id):
        target = db.session.query(cls).with_entities(cls.id).filter(cls.user_id == user_id).filter(cls.channel_id == channel_id).first()
        if not target:
            return False
        else:
            return True


class SlackMessage(db.Model):
    """
            作成者: kazu
            概要: Slack内メッセージを保存するテーブル
    """
    __tablename__ = 'slack_messages'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    team_id = db.Column(db.String(20), index=True, nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('slack_channels.id'))
    event_id = db.Column(db.String(20), nullable=False, unique=True)
    event_type = db.Column(db.String(20), index=True, nullable=False)
    event_time = db.Column(db.Integer, nullable=False)
    message_time = db.Column(db.Float(10))
    file_id = db.Column(db.String(20))
    file_name = db.Column(db.String(50))
    file_deleted = db.Column(db.Integer, default=0)
    text = db.Column(db.String(300))
    reaction = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, user_id, team_id, event_id, event_type, event_time, message_time, channel_id, text, file_id,
                 file_name, file_deleted, reaction, created_at,
                 updated_at):
        self.user_id = user_id
        self.team_id = team_id
        self.event_id = event_id
        self.event_type = event_type
        self.event_time = event_time
        self.message_time = message_time
        self.channel_id = channel_id
        self.text = text
        self.file_id = file_id
        self.file_name = file_name
        self.file_deleted = file_deleted
        self.reaction = reaction
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, user_id={self.user_id}, team_id={self.team_id}, event_id={self.event_id}, event_type={self.event_type}, " \
               f"event_time={self.event_time}, message_time={self.message_time}, " \
               f"channel_id={self.channel_id}, text={self.text}, file_id={self.file_id}, file_name={self.file_name}, " \
               f"file_deleted={self.file_deleted}, reaction={self.reaction}, create_at={self.created_at}, update_at=" \
               f"{self.updated_at} "

    @classmethod
    def insert_message(cls, user_id, channel_id, message_data):
        if 'edited' in message_data['event']:
            message_data['event']['type'] = 'message_edited'
            message_data['event']['event_ts'] = message_data['event']['edited']['ts']
        if 'files' in message_data['event']:
            for file in message_data['event']['files']:
                target = SlackMessage(user_id=user_id, team_id=message_data['team_id'], channel_id=channel_id,
                                      event_id=message_data['event_id'], event_type=message_data['event']['type'],
                                      event_time=message_data['event_time'],
                                      message_time=message_data['event']['event_ts'],
                                      text=message_data['event']['text'], file_id=file['id'], file_name=file['name'], file_deleted=0, reaction=None,
                                      created_at=datetime.now(), updated_at=datetime.now())
                db.session.add(target)
        else:
            target = SlackMessage(user_id=user_id, team_id=message_data['team_id'], channel_id=channel_id,
                              event_id=message_data['event_id'], event_type=message_data['event']['type'],
                              event_time=message_data['event_time'], message_time=message_data['event']['event_ts'],
                              text=message_data['event']['text'], file_id=None, file_name=None, file_deleted=0, reaction=None,
                              created_at=datetime.now(), updated_at=datetime.now())
            db.session.add(target)
        db.session.commit()
        return target

    @classmethod
    def insert_message_channel(cls, user_id, channel_id, message_data):
        target = SlackMessage(user_id=user_id, team_id=message_data['team_id'],
                              channel_id=channel_id, event_id=message_data['event_id'],
                              event_type=message_data['event']['type'], event_time=message_data['event_time'],
                              message_time=None, text=None, file_id=None, reaction=None, created_at=datetime.now(),
                              updated_at=datetime.now())
        db.session.add(target)
        db.session.commit()
        return target

    @classmethod
    def insert_message_file(cls, user_id, message_data):
        target = SlackMessage(user_id=user_id, team_id=message_data['team_id'],
                              channel_id=None, event_id=message_data['event_id'],
                              event_type=message_data['event']['type'], event_time=message_data['event_time'],
                              message_time=None, text=None, file_id=message_data['event']['file_id'], reaction=None,
                              created_at=datetime.now(), updated_at=datetime.now())
        db.session.add(target)
        db.session.commit()
        return target

    @classmethod
    def insert_message_reaction(cls, user_id, channel_id, message_data):
        target = SlackMessage(user_id=user_id, team_id=message_data['team_id'],
                              channel_id=channel_id, event_id=message_data['event_id'],
                              event_type=message_data['event']['type'], event_time=message_data['event_time'],
                              message_time=message_data['event']['item']['ts'], text=None, file_id=None,
                              reaction=message_data['event']['reaction'],
                              created_at=datetime.now(), updated_at=datetime.now())
        db.session.add(target)
        db.session.commit()
        return target

    @classmethod
    def insert_message_join(cls, user_id, channel_id, message_data):
        target = SlackMessage(user_id=user_id, team_id=message_data['team_id'],
                              channel_id=channel_id, event_id=message_data['event_id'],
                              event_type=message_data['event']['type'], event_time=message_data['event_time'],
                              message_time=None, text=None, file_id=None,
                              reaction=None,
                              created_at=datetime.now(), updated_at=datetime.now())
        db.session.add(target)
        db.session.commit()
        return target

    @classmethod
    def delete_file(cls, file_id):
        target = db.session.query(cls).filter(cls.file_id == file_id).first()
        target.file_deleted = 1
        target.updated_at = datetime.now()
        db.session.commit()
        return target

    @classmethod
    def check_duplicate(cls, message_data):
        target = db.session.query(cls).with_entities(cls.id).filter(cls.event_id == message_data['event_id']).first()
        if not target:
            return False
        else:
            return True



# zoomのアクセストークン
# TO DO: 暗号化
class ZoomAccessToken(db.Model):
    __tablename__ = 'zoom_access_tokens'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    access_token = db.Column(db.String(1000), nullable=False)
    refresh_token = db.Column(db.String(1000), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, user_id, access_token, refresh_token, created_at, updated_at):
        self.user_id = user_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, user_id = {self.user_id}, access_token = {self.access_token}, refresh_token = {self.refresh_token}, create_at={self.created_at}, update_at={self.updated_at} "

    @classmethod
    def get_access_token(cls, user_id):
        return db.session.query(cls).with_entities(cls.access_token).filter(cls.user_id == user_id).first()
        # return cls.query.with_entities(
        #     cls.access_token
        # ).filter(cls.user_id == user_id).first()

    @classmethod
    def get_refresh_token(cls, user_id):
        return db.session.query(cls).with_entities(cls.refresh_token).filter(cls.user_id == user_id).first()
        # return cls.query.with_entities(
        #     cls.refresh_token
        # ).filter(cls.user_id == user_id).first()

    @classmethod
    def update_access_token(cls, user_id, access_token, refresh_token):
        target = db.session.query(ZoomAccessToken).filter(cls.user_id == user_id).first()
        target.access_token = access_token
        target.refresh_token = refresh_token
        target.updated_at = datetime.now()
        db.session.commit()
        # db_cur.execute(
        #     "UPDATE zoom_access_tokens SET access_token=%s, refresh_token=%s, updated_at=%s WHERE user_id = %s",
        #     (access_token, refresh_token, datetime.now(), user_id))

    # @classmethod
    # def insert_message(self):
    #     print(self.created_at)
    #     db.session.add(self)


class ZoomMeeting(db.Model):
    __tablename__ = 'zoom_meetings'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),  # チェック制約
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    meeting_id = db.Column(db.String(30), nullable=False, unique=True)
    meeting_uuid = db.Column(db.String(50), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    meeting_created = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    zoom_participant = db.relationship('ZoomParticipant', backref='meeting', lazy=True)

    # zoom_meeting = db.relationship('ZoomMessage', backref='meeting', lazy=True)
    # zoom_recording = db.relationship('ZoomRecording', backref='meeting', lazy=True)

    def __init__(self, user_id, meeting_id, meeting_uuid, topic, start_time, duration, meeting_created, created_at,
                 updated_at):
        self.user_id = user_id
        self.meeting_id = meeting_id
        self.meeting_uuid = meeting_uuid
        self.topic = topic
        self.start_time = start_time
        self.duration = duration
        self.meeting_created = meeting_created
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, user_id = {self.user_id}, meeting_id = {self.meeting_id}, meeting_uuid = {self.meeting_uuid}, topic = {self.topic}, start_time = {self.start_time}, duration = {self.duration}, meeting_created = {self.meeting_created}, create_at={self.created_at}, update_at={self.updated_at} "

    @classmethod
    def insert_schedule(cls, user_id, meeting):
        target = ZoomMeeting(user_id=user_id, meeting_id=meeting['id'],
                             meeting_uuid=meeting['uuid'], topic=meeting['topic'],
                             start_time=meeting['start_time'], duration=meeting['duration'],
                             meeting_created=meeting['created_at'], created_at=datetime.now(),
                             updated_at=datetime.now())
        db.session.add(target)
        db.session.commit()
        return target
        # db_cur.execute(
        #     "INSERT INTO zoom_meetings(user_id, meeting_id, meeting_uuid, topic, start_time, duration, meeting_created, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        #     (user_id, meeting['id'], meeting['uuid'], meeting['topic'], meeting['start_time'], meeting['duration'], meeting['created_at'], datetime.now(), datetime.now()))

    @classmethod
    def check_meeting_uuid(cls, meeting_uuid):
        return cls.query.with_entities(
            cls.id
        ).filter(cls.meeting_uuid == meeting_uuid).first()

    @classmethod
    def select_meeting(cls, user_id):
        return db.session.query(cls).with_entities(cls.meeting_id, cls.topic, cls.start_time, cls.duration,
                                                   cls.meeting_created).filter(cls.user_id == user_id).all()

    # @classmethod
    # def insert_message(self):
    #     print(self.created_at)
    #     db.session.add(self)


class ZoomParticipant(db.Model):
    __tablename__ = 'zoom_participants'
    __table_args__ = (
        CheckConstraint('updated_at >= created_at'),
        UniqueConstraint('zoom_user_id', 'meeting_id'),
    )
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    meeting_id = db.Column(db.Integer, db.ForeignKey('zoom_meetings.id'), unique=True)
    zoom_user_id = db.Column(db.String(50), nullable=False)
    zoom_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)

    def __init__(self, user_id, meeting_id, zoom_user_id, zoom_name, created_at, updated_at):
        self.user_id = user_id
        self.meeting_id = meeting_id
        self.zoom_user_id = zoom_user_id
        self.zoom_name = zoom_name
        self.created_at = created_at
        self.updated_at = updated_at

    def __str__(self):
        return f"id = {self.id}, user_id = {self.user_id}, meeting_id = {self.meeting_id}, zoom_user_id = {self.zoom_user_id}, zoom_name = {self.zoom_name} create_at={self.created_at}, update_at={self.updated_at} "

    @classmethod
    def insert_participant(cls, user_id, meeting_id, participant):
        target = ZoomMeeting(user_id=user_id, meeting_id=meeting_id, zoom_user_id=participant['id'],
                             zoom_name=participant['name'], created_at=datetime.now(), updated_at=datetime.now())
        db.session.add(target)
        db.session.commit()
        # db_cur.execute(
        #     "INSERT INTO zoom_meetings(user_id, meeting_id, zoom_user_id, zoom_name, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s)",
        #     (user_id, meeting_id, participant['id'], participant['name'], datetime.now(), datetime.now()))

# class ZoomMessage(db.Model):
#     __tablename__ = 'zoom_messages'
#     __table_args__ = (
#         CheckConstraint('updated_at >= created_at'),  # チェック制約
#     )
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
#     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
#     meeting_id = db.Column(db.Integer, db.ForeignKey('zoom_meetings.id'), nullable=False)
#     message = db.Column(db.String(500), nullable=False)
#     time = db.Column(db.DateTime, nullable=False)
#     created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
#     updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
#
#     def __init__(self, user_id, meeting_id, message, time, created_at, updated_at):
#         self.user_id = user_id
#         self.meeting_id = meeting_id
#         self.message = message
#         self.time = time
#         self.created_at = created_at
#         self.updated_at = updated_at
#
#     def __str__(self):
#         return f"id = {self.id}, user_id = {self.user_id}, meeting_id = {self.meeting_id}, message = {self.message}, time = {self.time}, create_at={self.created_at}, update_at={self.updated_at} "
#
#
# class ZoomRecording(db.Model):
#     __tablename__ = 'zoom_recordings'
#     __table_args__ = (
#         CheckConstraint('updated_at >= created_at'),  # チェック制約
#     )
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主キー
#     meeting_id = db.Column(db.Integer, db.ForeignKey('zoom_meetings.id'), nullable=False)
#     start = db.Column(db.DateTime, nullable=False)
#     end = db.Column(db.DateTime, nullable=False)
#     url = db.Column(db.String(200), nullable=False)
#     created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
#     updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
#
#     def __init__(self, meeting_id, start, end, url, created_at, updated_at):
#         self.meeting_id = meeting_id
#         self.start = start
#         self.end = end
#         self.url = url
#         self.created_at = created_at
#         self.updated_at = updated_at
#
#     def __str__(self):
#         return f"id = {self.id}, meeting_id = {self.meeting_id}, start = {self.start}, end = {self.end}, url = {self.url},  create_at={self.created_at}, update_at={self.updated_at} "
