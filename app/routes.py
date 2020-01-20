from flask import render_template, flash, redirect, url_for, request
from app import app
from app import app, db, pwd
from app.forms import RegForm, LoginForm
from app.models import load_user, User, UserData, ResumeUploads, LetterUploads, VideoUploads, AudioUploads
from app.utils.text_analysis import get_article_stats
from app.utils.utils import allowed_file, allowed_filesize
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
import os
import urllib.request
import textract



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
    if UserData.query.filter_by(user_id=current_user.get_id()).all():
        print(UserData.query.filter_by(user_id=current_user.get_id()).order_by(UserData.sno.desc()).first())
    else:
        pass
    return render_template("admin.html")


# Authorization


@app.route("/signup" , methods = ['GET' , 'POST'])
def signuppage() :
    if current_user.is_authenticated :
        flash("You are already logged in." , "warning")
        return redirect(url_for("homepage"))
    form = RegForm(request.form)
    if request.method == "POST" and form.validate():
        hashed = pwd.generate_password_hash(form.password.data).decode('utf-8')
        form_data = User(uname=form.uname.data, email=form.email.data, password=hashed)
        db.session.add(form_data)
        db.session.commit()
        flash("Account created for %s!" % (form.uname.data), "primary")
        return redirect(url_for("loginpage"))
    return render_template("signup.html" , form = form)


@app.route("/login" , methods = ['GET' , 'POST'])
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
    logout_user()
    flash("Successfuly logged out." , "primary")
    return redirect(url_for("homepage"))


# Uploads


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
    pass


# AI Analytics


@app.route("/text_stats", methods = ['GET'])
def text_stats():
    text = textract.process("letter.docx").decode('utf-8')
    return get_article_stats(text)

