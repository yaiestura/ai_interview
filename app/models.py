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
    resume_uploads = db.relationship('ResumeUploads', backref='user', lazy=True)
    letter_uploads = db.relationship('LetterUploads', backref='user', lazy=True)
    video_uploads = db.relationship('VideoUploads', backref='user', lazy=True)
    audio_uploads = db.relationship('AudioUploads', backref='user', lazy=True)

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

class ResumeUploads(db.Model):
    __tablename__ = 'resumeuploads'
    sno = db.Column(db.Integer, primary_key=True)
    is_resume_uploaded = db.Column(db.Boolean, default=False, nullable=True)
    is_resume_processed = db.Column(db.Boolean, default=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.sno'), nullable=False)

    def __repr__(self):
        return 'ResumeUploads(%s, %s, %s)' % (self.is_resume_uploaded, self.is_resume_processed, self.user_id)

class LetterUploads(db.Model):
    __tablename__ = 'letteruploads'
    sno = db.Column(db.Integer, primary_key=True)
    is_letter_uploaded = db.Column(db.Boolean, default=False, nullable=True)
    is_letter_processed = db.Column(db.Boolean, default=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.sno'), nullable=False)

    def __repr__(self):
        return f'LetterUploads({self.is_letter_uploaded}, {self.is_letter_processed}, {self.user_id})'

class VideoUploads(db.Model):
    __tablename__ = 'videouploads'
    sno = db.Column(db.Integer, primary_key=True)
    is_video_uploaded = db.Column(db.Boolean, default=False, nullable=True)
    is_video_processed = db.Column(db.Boolean, default=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.sno'), nullable=False)

    def __repr__(self):
        return f'VideoUploads({self.is_video_uploaded}, {self.is_video_processed}, {self.user_id})'

class AudioUploads(db.Model):
    __tablename__ = 'audiouploads'
    sno = db.Column(db.Integer, primary_key=True)
    is_audio_uploaded = db.Column(db.Boolean, default=False, nullable=True)
    is_audio_processed = db.Column(db.Boolean, default=False, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.sno'), nullable=False)

    def __repr__(self):
        return f'AudioUploads({self.is_audio_uploaded}, {self.is_audio_processed}, {self.user_id})'


# class Statistics(db.Model):
#     __tablename__ = 'statistics'

#     def __repr__(self):
#         pass