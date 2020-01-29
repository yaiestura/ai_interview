from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from celery import Celery

app = Flask(__name__, static_folder='static', template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config["ALLOWED_FILE_EXTENSIONS"] = ["PDF", "DOC", "DOCX"]
app.config["ALLOWED_VIDEO_EXTENSIONS"] = ["MP4", "AVI", "MKV"]
app.config["ALLOWED_AUDIO_EXTENSIONS"] = ["MP3"]
app.config["MAX_FILESIZE"] = 20 * 1024 * 1024
app.config["MAX_VIDEO_FILESIZE"] = 50 * 1024 * 1024
app.config["MAX_AUDIO_FILESIZE"] = 50 * 1024 * 1024

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

db = SQLAlchemy(app)
pwd = Bcrypt(app)

login_manager = LoginManager(app)

login_manager.login_view = "loginpage"
login_manager.login_message = "You are not authorised to access this page. Please login first."
login_manager.login_message_category = "danger"

from app import routes