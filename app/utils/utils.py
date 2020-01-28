import os
import shutil
import glob

from app import app, db
from app.models import UserData

from flask_login import current_user



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
        path = os.path.join(os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/video')
        shutil.rmtree(path)
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

