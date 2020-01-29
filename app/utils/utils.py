import os
import shutil
import glob

from app import app, db
from app.models import User, UserData, Statistics

from flask_login import current_user


def count_documents_uploaded(username):

    query = UserData.query.filter_by(user_id=username).order_by(UserData.sno.desc()).first()

    resume_uploaded = 1 if query.user_resume else 0
    letter_uploaded = 1 if query.user_letter else 0
    audio_uploaded = 1 if query.user_audio else 0
    video_uploaded = 1 if query.user_video else 0

    return resume_uploaded + letter_uploaded + audio_uploaded + video_uploaded


# Folders


def empty_folder(directory):
    content = glob.glob(directory)
    for f in content:
        os.remove(f)

def is_folder_empty(directory):
    return True if (not os.listdir(directory)) else False


# Files


def allowed_file(filename, extensions):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in extensions:
        return True
    else:
        return False


def allowed_filesize(filesize, limit):

    if int(filesize) <= limit:
        return True
    else:
        return False


def delete_document_from_db(type):
    if type == "Resume":
        resume = UserData(
            user_resume = None,
            user_letter = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_letter,
            user_video = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_video,
            user_audio = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_audio,
            user_id = current_user.get_id()
        )
        db.session.add(resume)
        db.session.commit()
        path = os.path.join(os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/resume')
        shutil.rmtree(path)
        os.remove(os.path.join(
            os.path.dirname(app.instance_path), f'app/resume/res_data.txt'))
        os.remove(os.path.join(
            os.path.dirname(app.instance_path), f'app/resume/res_score.txt'))

    if type == "CV":
        letter = UserData(
            user_resume = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_resume,
            user_letter = None,
            user_video = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_video,
            user_audio = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_audio,
            user_id = current_user.get_id()
        )
        db.session.add(letter)
        db.session.commit()
        path = os.path.join(os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/letter')
        shutil.rmtree(path)

    if type == "Video":
        video = UserData(
            user_resume = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_resume,
            user_letter = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_letter,
            user_video = None,
            user_audio = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_audio,
            user_id = current_user.get_id()
        )
        db.session.add(video)
        db.session.commit()
        video_path = os.path.join(os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/video')
        vid_analysis_path = os.path.join(
            os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/video_analysis'
        )
        shutil.rmtree(video_path)
        shutil.rmtree(vid_analysis_path)
        if os.path.exists('app/utils/emotion_detection/emotions.txt'):
            f = open('app/utils/emotion_detection/emotions.txt', 'r+')
            f.truncate(0)
        if os.path.exists('app/utils/blinks.txt'):
            f = open('app/utils/blinks.txt', 'r+')
            f.truncate(0)

    if type == "Audio":
        audio = UserData(
            user_resume = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_resume,
            user_letter = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_letter,
            user_video = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_video,
            user_audio = None,
            user_id = current_user.get_id()
        )
        db.session.add(audio)
        db.session.commit()
        path = os.path.join(os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/audio')
        shutil.rmtree(path)

