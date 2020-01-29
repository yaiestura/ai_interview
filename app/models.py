from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    sno = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.now())
    uname = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    userdata = db.relationship('UserData', backref='user', lazy=True)
    statistics = db.relationship('Statistics', backref='user', lazy=True)


    def get_id(self):
        try:
            return (self.sno)
        except AttributeError:
            raise NotImplementedError('No `id` attribute - override `get_id`')

    def __repr__(self):
        return  'User(%s, %s)' % (self.uname, self.email)

class UserData(db.Model):
    __tablename__ = 'userdata'
    sno = db.Column(db.Integer, primary_key=True)
    user_resume = db.Column(db.String(150), default=None, nullable=True)
    user_letter = db.Column(db.String(150), default=None, nullable=True)
    user_video = db.Column(db.String(150), default=None, nullable=True)
    user_audio = db.Column(db.String(150), default=None, nullable=True)
    time = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.sno'), nullable=False)


    def __repr__(self):
        return  'UserData(%s, %s, %s, %s, %s, %s)' % (self.user_resume, self.user_letter, self.user_video, self.user_audio, self.time, self.user_id)


class Statistics(db.Model):
    __tablename__ = 'statistics'
    sno = db.Column(db.Integer, primary_key=True)
    blink_count = db.Column(db.Integer, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.sno'), nullable=False)

    def __repr__(self):
        return  'Statistics(%s, %s, %s)' % (self.sno, self.blink_count, self.user_id)