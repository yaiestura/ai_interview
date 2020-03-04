from flask import render_template, flash, session, redirect, url_for, request, Response, send_from_directory, send_file
from app import app
from app import app, db, pwd, celery
from app.forms import RegForm, LoginForm
from app.models import load_user, User, UserData, Statistics
from app.utils.camera import VideoCamera
from app.utils.text_analysis import cv_analysis, audio_sentiment_analysis
from app.utils.audio_analysis import transcribe_audio_to_text
from app.utils.eye_tracking import eye_tracking
from app.utils.head_tracking import head_movement_estimation
from app.utils.audio_sentiment.sentiment import audio_emotion_analysis
from app.utils.emotion_detection.emotion import video_emotion_detection
from app.utils.generate_report import generate_report
from app.utils.utils import allowed_file, allowed_filesize, delete_document_from_db, count_documents_uploaded
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from collections import Counter
import os
import urllib.request
import textract
import requests
import subprocess



# Routes
@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")


@app.route('/')
def homepage():
    return render_template("information.html")


@app.route('/documentation')
def documentation():
    return render_template("documentation.html")


@app.route("/dashboard")
@login_required
def dashboard():

    query = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first()
    user_query = User.query.filter_by(sno=current_user.get_id()).first()
    users_number = User.query.count()
    documents = count_documents_uploaded(current_user.get_id())

    def is_uploaded(query_type):
        return 'No' if query_type == None else 'Yes'

    def get_count(q):
        count_q = q([func.count()]).order_by(None)
        count = q.session.execute(count_q).scalar()
        return count

    admin_uploads_data = {
        'is_resume_uploaded': is_uploaded(query.user_resume) if query else 'No',
        'is_letter_uploaded': is_uploaded(query.user_letter) if query else 'No',
        'is_video_uploaded': is_uploaded(query.user_video) if query else 'No',
        'is_audio_uploaded': is_uploaded(query.user_audio) if query else 'No'
    };

    return render_template("admin.html", uploads=admin_uploads_data,
    time=str(user_query.time).split(".")[0].split(" ")[0],
    documents=documents, users_number=users_number)


@app.route('/profile/<username>')
def profile(username):
	return 'username is %s' % username


# Authorization


@app.route("/signup", methods = ['GET' , 'POST'])
def signuppage() :
    # If user is already logged in, flash a notification
    # and redirect him to home page
    if current_user.is_authenticated :
        flash("You are already logged in." , "warning")
        return redirect(url_for("homepage"))

    # Create an authentication form for sign up
    form = RegForm(request.form)
    # Recieve data from a browser form and validate the data
    if request.method == "POST" and form.validate():
        # Hash the password to store in database
        hashed = pwd.generate_password_hash(form.password.data).decode('utf-8')
        # Save a new User and his credentials into the database
        form_data = User(uname=form.uname.data, email=form.email.data, password=hashed)
        db.session.add(form_data)
        db.session.commit()
        # Account is created, and user redirected to login page
        flash("Account created for %s!" % (form.uname.data), "primary")
        return redirect(url_for("loginpage"))
    return render_template("signup.html" , form = form)


@app.route("/login", methods = ['GET' , 'POST'])
def loginpage():
    if current_user.is_authenticated :
        flash("You are already logged in." , "warning")
        return redirect(url_for("homepage"))
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        member = User.query.filter_by(email = form.email.data).first()
        if member and pwd.check_password_hash(member.password , form.password.data) :
            login_user(member)
            flash("Welcome, %s!" % (form.email.data) , "primary")
            return redirect(url_for("dashboard"))
        else :
            flash("Email or Password doesn't match, please try again." , "danger")
            return redirect(url_for("loginpage"))
    return render_template("login.html" , form = form)


@app.route("/logout")
@login_required
def logoutpage():
    session.clear()
    logout_user()
    flash("Successfuly logged out." , "primary")
    return redirect(url_for("homepage"))


# Database Manipulations


@app.route('/delete_file/<type>', methods = ['GET', 'POST'])
@login_required
def delete_file(type):
    delete_document_from_db(type)
    flash(f"{type} was successfully deleted", "info")
    return show_uploads()


# Uploads


@app.route('/uploads', methods = ['GET', 'POST'])
@login_required
def uploads():
    if request.method == "POST":
        print(request.form['document'])

    if request.method == "GET":
        global show_uploads

        def show_uploads():
            query = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first()

            def is_uploaded(query_type):
                return 'No' if query_type == None else 'Yes'


            uploads_data = (
            {'type': 'Resume',
            'path': query.user_resume if query else 'None',
            'uploaded': is_uploaded(query.user_resume) if query else 'No' },
            {'type': 'CV',
            'path': query.user_letter if query else 'None',
            'uploaded': is_uploaded(query.user_letter) if query else 'No' },
            {'type': 'Video',
            'path': query.user_video if query else 'None',
            'uploaded': is_uploaded(query.user_video) if query else 'No' },
            {'type': 'Audio',
            'path': query.user_audio if query else 'None',
            'uploaded': is_uploaded(query.user_audio) if query else 'No'  }
            );

            return render_template("dashboard/uploads.html", uploads=uploads_data)

        return show_uploads()


@app.route('/upload_resume', methods = ['GET', 'POST'])
@login_required
def upload_resume():
    if request.method == "POST":
        if request.files:
            if "filesize" in request.cookies:
                if not allowed_filesize(request.cookies["filesize"], app.config["MAX_FILESIZE"]):
                    flash('Filesize exceeded maximum limit', "danger")
                    return redirect(request.url)

                document = request.files["file"]
                if document.filename == "":
                    flash('No filename', "danger")
                    return redirect(request.url)

                if allowed_file(document.filename, app.config["ALLOWED_FILE_EXTENSIONS"]):

                    directory = os.path.join(
                        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/resume'
                    )
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    # filename = secure_filename(file.filename)
                    document.save(os.path.join(directory, document.filename))
                    resume = UserData(
                        user_resume=f'{directory}/{document.filename}',
                        user_letter=UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_letter if UserData.query.filter_by(user_id=current_user.get_id()).all() else None,
                        user_video=UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_video if UserData.query.filter_by(user_id=current_user.get_id()).all() else None,
                        user_audio=UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_audio if UserData.query.filter_by(user_id=current_user.get_id()).all() else None,
                        user_id=current_user.get_id()
                    )
                    db.session.add(resume)
                    db.session.commit()

                    flash(f'Document uploaded successfully,\n{document.filename}', "info")

                    resume_file = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_resume

                    resume_analyzer.delay(resume_file)

                    return redirect(request.url)

                else:
                    flash('That file extension is not allowed', "danger")
                    return redirect(request.url)

    return render_template("dashboard/upload_resume.html")


@app.route('/upload_letter', methods = ['GET', 'POST'])
@login_required
def upload_letter():
    if request.method == "POST":
        if request.files:
            if "filesize" in request.cookies:
                if not allowed_filesize(request.cookies["filesize"], app.config["MAX_FILESIZE"]):
                    flash('Filesize exceeded maximum limit', "danger")
                    return redirect(request.url)

                document = request.files["file"]
                if document.filename == "":
                    flash('No filename', "danger")
                    return redirect(request.url)

                if allowed_file(document.filename, app.config["ALLOWED_FILE_EXTENSIONS"]):

                    directory = os.path.join(
                        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/letter'
                    )
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    # filename = secure_filename(file.filename)
                    document.save(os.path.join(directory, document.filename))
                    letter = UserData(
                        user_resume=UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_resume if UserData.query.filter_by(user_id=current_user.get_id()).all() else None,
                        user_letter=f'{directory}/{document.filename}',
                        user_video=UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_video if UserData.query.filter_by(user_id=current_user.get_id()).all() else None,
                        user_audio=UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_audio if UserData.query.filter_by(user_id=current_user.get_id()).all() else None,
                        user_id=current_user.get_id()
                    )
                    db.session.add(letter)
                    db.session.commit()

                    flash(f'Document uploaded successfully,\n{document.filename}', "info")

                    return redirect(request.url)

                else:
                    flash('That file extension is not allowed', "danger")
                    return redirect(request.url)

    return render_template("dashboard/upload_letter.html")


@app.route('/upload_video', methods = ['GET', 'POST'])
@login_required
def upload_video():
    if request.method == "POST":
        if request.files:
            if "filesize" in request.cookies:
                if not allowed_filesize(request.cookies["filesize"], app.config["MAX_VIDEO_FILESIZE"]):
                    flash('Filesize exceeded maximum limit', "danger")
                    return redirect(request.url)

                document = request.files["file"]
                if document.filename == "":
                    flash('No filename', "danger")
                    return redirect(request.url)

                if allowed_file(document.filename, app.config["ALLOWED_VIDEO_EXTENSIONS"]):

                    directory = os.path.join(
                        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/video'
                    )
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    # filename = secure_filename(file.filename)
                    document.save(os.path.join(directory, document.filename))
                    video = UserData(
                        user_resume=UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_resume if UserData.query.filter_by(user_id=current_user.get_id()).all() else None,
                        user_letter=UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_letter if UserData.query.filter_by(user_id=current_user.get_id()).all() else None,
                        user_video=f'{directory}/{document.filename}',
                        user_audio=UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_audio if UserData.query.filter_by(user_id=current_user.get_id()).all() else None,
                        user_id=current_user.get_id()
                    )
                    db.session.add(video)
                    db.session.commit()

                    flash(f'Video uploaded successfully,\n{document.filename}', "info")

                    video_file = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_video

                    save_directory = os.path.join(
                        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/video_analysis'
                    )
                    if not os.path.exists(save_directory):
                        os.makedirs(save_directory)

                    eyes_tracking.delay(video_file, save_directory)
                    emotion_detection.delay(video_file, save_directory)
                    head_detection.delay(video_file, save_directory)

                    return redirect(request.url)

                else:
                    flash('That file extension is not allowed', "danger")
                    return redirect(request.url)

    return render_template("dashboard/upload_video.html")


@app.route('/upload_audio', methods = ['GET', 'POST'])
@login_required
def upload_audio():
    if request.method == "POST":
        if request.files:
            if "filesize" in request.cookies:
                if not allowed_filesize(request.cookies["filesize"], app.config["MAX_AUDIO_FILESIZE"]):
                    flash('Filesize exceeded maximum limit', "danger")
                    return redirect(request.url)

                document = request.files["file"]
                if document.filename == "":
                    flash('No filename', "danger")
                    return redirect(request.url)

                if allowed_file(document.filename, app.config["ALLOWED_AUDIO_EXTENSIONS"]):

                    directory = os.path.join(
                        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/audio'
                    )
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    # filename = secure_filename(file.filename)
                    document.save(os.path.join(directory, document.filename))
                    audio = UserData(
                        user_resume=UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_resume if UserData.query.filter_by(user_id=current_user.get_id()).all() else None,
                        user_letter=UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_letter if UserData.query.filter_by(user_id=current_user.get_id()).all() else None,
                        user_video=UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_video if UserData.query.filter_by(user_id=current_user.get_id()).all() else None,
                        user_audio=f'{directory}/{document.filename}',
                        user_id=current_user.get_id()
                    )
                    db.session.add(audio)
                    db.session.commit()

                    flash(f'Audio uploaded successfully,\n{document.filename}', "info")

                    return redirect(request.url)

                else:
                    flash('That file extension is not allowed', "danger")
                    return redirect(request.url)

    return render_template("dashboard/upload_audio.html")


@app.route('/record_video', methods = ['GET', 'POST'])
@login_required
def record_video():
    if request.method == "POST":
        pass

    return render_template("dashboard/record_video.html")


@app.route('/images/<path:filename>')
def send_image(filename):

    directory = os.path.join(
        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/text_analytics/'
    )

    return send_from_directory(directory, filename, as_attachment=True)

# Utils


@app.route('/video_feed', methods = ['GET', 'POST'])
@login_required
def video_feed():

    def gen(camera):
        while True:
            frame = camera.get_frame()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/stream_audio')
def stream_audio():

    audio = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_audio

    directory, filename = audio.rsplit('/',1)[0], audio.rsplit('/',1)[1]

    return send_from_directory(directory, filename)


@app.route('/stream_video/<filename>')
def stream_video(filename):

    directory = os.path.join(
        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/video_analysis'
    )
    print(filename)

    return send_from_directory(directory, filename)


@app.route('/download_report')
def download_report():

    directory = os.path.join(
        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/reports'
    )

    if not os.path.exists(directory):
        os.makedirs(directory)

    url = generate_report(current_user.uname)

    return send_file(url, as_attachment=False, cache_timeout=0)


#Celery Asynchronous Tasks


@celery.task
def eyes_tracking(video_file, save_directory):
    return eye_tracking(video_file, save_directory)


@celery.task
def emotion_detection(video_file, save_directory):
    return video_emotion_detection(video_file, save_directory)


@celery.task
def head_detection(video_file, save_directory):
    return head_movement_estimation(video_file, save_directory)


@celery.task
def blinking_tracking(video_file):
    subprocess.call(['python3', 'app/utils/detect_blinks.py',
    '--shape-predictor', 'app/utils/shape_predictor_68_face_landmarks.dat',
    '--video', video_file], shell=False)


@celery.task
def resume_analyzer(resume_path):
    #python3 main.py --type fixed "path" --model_name model
    subprocess.call(['python3', 'app/resume/main.py',
    '--type', 'fixed', resume_path,
    '--model_name', 'model'], shell=False)


# AI Analytics


@app.route("/resume_analysis", methods = ['GET'])
@login_required
def resume_analysis():

    content_exists = True if os.path.exists("app/resume/res_data.txt") else False
    score_exists = True if os.path.exists("app/resume/res_score.txt") else False
    if content_exists:
        with open("app/resume/res_data.txt", "r") as f:
            content = f.read()
    if score_exists:
        with open("app/resume/res_score.txt", "r") as f:
            score = f.read()

    if content_exists and score_exists:

        return render_template("assessment/resume.html",
        content=content, score=score, content_exists=content_exists)

    else:
        return render_template("assessment/resume.html",
        content=None, score=None, content_exists=None)


@app.route("/letter_analysis", methods = ['GET'])
@login_required
def letter_analysis():

    directory = os.path.join(
        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/text_analytics'
    )

    letter = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_letter

    if letter:
        sentiment_data, text_data = cv_analysis(letter)
        print(sentiment_data)

        return render_template("assessment/motivational.html",
        sentiment_data=sentiment_data, text_data=text_data, directory=directory)

    else:
        return render_template("assessment/motivational.html",
        sentiment_data=None, text_data=None, directory=None)


@app.route("/audio_analysis", methods = ['GET'])
@login_required
def audio_analysis():

    directory = os.path.join(
        os.path.dirname(app.instance_path), f'app/userdata/{current_user.uname}/text_analytics'
    )

    audio_file = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_audio

    if audio_file:
        transcript = transcribe_audio_to_text(audio_file).title()

        sentiment_data = audio_sentiment_analysis(transcript)
        emotion_data = audio_emotion_analysis(audio_file)

        return render_template("assessment/audio.html", transcript=transcript, sentiment=sentiment_data, emotion=emotion_data)

    return render_template("assessment/audio.html", transcript=None, sentiment=None, emotion=None)


@app.route("/video_analysis", methods = ['GET'])
@login_required
def video_analysis():

    video_file = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_video

    eye_tracking = True if os.path.exists(os.path.join(
        os.path.dirname(app.instance_path),
        f'app/userdata/{current_user.uname}/video_analysis/output.webm'
    )) else False
    blink_tracking = True if os.path.exists(os.path.join(
        os.path.dirname(app.instance_path),
        f'app/userdata/{current_user.uname}/video_analysis/blink.webm'
    )) else False
    emotion_detection = True if os.path.exists(os.path.join(
        os.path.dirname(app.instance_path),
        f'app/userdata/{current_user.uname}/video_analysis/emotion.webm'
    )) else False
    head_detection = True if os.path.exists(os.path.join(
        os.path.dirname(app.instance_path),
        f'app/userdata/{current_user.uname}/video_analysis/head.webm'
    )) else False


    if video_file:
        return render_template("assessment/video.html", video_file=video_file, eye_tracking=eye_tracking, emotion=emotion_detection, head=head_detection)
    else:
        return render_template("assessment/video.html", video_file=None, eye_tracking=None, emotion=None, head=None)


@app.route('/statistics')
def statistics():

    query = Statistics.query.filter_by(user_id=current_user.get_id()).order_by(Statistics.sno.desc()).first()

    blink_num = query.blink_count if query else None

    if os.path.exists('app/utils/emotion_detection/emotions.txt'):
        with open('app/utils/emotion_detection/emotions.txt') as f:
            emotions = f.read().splitlines()

        emotions_data = dict((x, "%.2f" % ((emotions.count(x) * 100.0) / len(emotions))) for x in set(emotions))

    return render_template("assessment/statistics.html", emotions=emotions_data, blinks=blink_num)


@app.route('/blinking_counter')
def blinking_counter():

    video_file = UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first().user_video

    if video_file:
        if os.path.exists('app/utils/blinks.txt') and os.stat('app/utils/blinks.txt').st_size != 0:
            with open('app/utils/blinks.txt') as f:
                blinks = f.read().splitlines()

            stats = Statistics(blink_count=blinks[-1], user_id=current_user.get_id())

            db.session.add(stats)
            db.session.commit()

            return render_template("assessment/blink.html", blink=blinks[-1], video=True)

        else:

            blinking_tracking.delay(video_file)
            flash("Blinking counter has finished working","info")

            return render_template("assessment/blink.html", blink=None, video=True)

    else:

        return render_template("assessment/blink.html", blink=None, video=False)