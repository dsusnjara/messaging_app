from datetime import datetime
from app import app
from flask import render_template, request, make_response, redirect, url_for, flash
from app.models import db, User, Message
import hashlib
from app.forms import LoginForm, RegistrationForm, EditProfileForm
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
@login_required
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        # noinspection PyArgumentList
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("You have registered your account successfully.")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password_hash(form.password.data):
            flash("Invalid username or password.")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/send", methods=["GET", "POST"])
def send():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    if request.method == "GET":
        name = User.name
        users = db.query(User).filter_by(name=name).all()
        return render_template("send.html", users=users, user=user)

    elif request.method == "POST":
        send_message = request.form.get("message")
        sender_id = user.id
        receiver_id = request.form.get("user")
        title = request.form.get("title")

        message = Message(message=send_message, title=title, sender_id=sender_id, receiver_id=receiver_id)

        db.add(message)
        db.commit()

        return redirect(url_for("index", user=user))


@app.route("/received", methods=["GET"])
def received():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    user_id = user.id
    received_messages = db.query(Message).filter_by(receiver_id=user_id).all()
    return render_template("received.html", received_messages=received_messages, user=user)


@app.route("/sent", methods=["GET", "POST"])
def sent():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    user_id = user.id
    sent_messages = db.query(Message).filter_by(sender_id=user_id).all()
    return render_template("sent.html", sent_messages=sent_messages, user=user)


@app.route("/message/<message_id>", methods=["GET"])
def message(message_id):
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    message = db.query(Message).get(int(message_id))
    return render_template("message.html", message=message, user=user)


@app.route("/message/<message_id>/delete", methods=["POST"])
def message_delete(message_id):
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    message = db.query(Message).get(int(message_id))
    if user.id == message.receiver_id:
        db.delete(message)
        db.commit()
        return redirect(url_for("received"))
    return redirect(url_for("received"))


@app.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template("user.html", title=f"{user.username}", user=user)


@app.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data= current_user.about_me
    return render_template("edit_profile.html", title="Edit Profile", form=form)


@app.route("/profile/delete", methods=["GET", "POST"])
def profile_delete():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        if user:
            return render_template("profile_delete.html", user=user)
        else:
            return redirect(url_for("index"))

    elif request.method == "POST":
        db.delete(user)
        db.commit()

        return redirect(url_for("index"))


@app.before_request
def before_request():
    """Update user's last_seen attribute on every request made."""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))