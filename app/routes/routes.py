from datetime import datetime
from app import app
from flask import render_template, request, redirect, url_for, flash, g
from app.models import db, User, Message
from app.forms import EditProfileForm, MessageForm
from flask_login import current_user, login_required


@app.route("/", methods=["GET"])
@app.route("/index", methods=["GET"])
@login_required
def index():
    return render_template("index.html", title="Home Page")


@app.route("/send", methods=["GET", "POST"])
@login_required
def send():
    form = MessageForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        send_to = form.send_to.data

        receiver = User.query.filter_by(username=send_to).first()

        message = Message(title=title, body=body, sender_id=current_user.id, receiver_id=receiver.id)
        db.session.add(message)
        db.session.commit()
        flash(f"Your message has been sent to {receiver.username}")
        return redirect(url_for("index"))

    return render_template("send.html", form=form)


@app.route("/received", methods=["GET"])
@login_required
def received():
    received_messages = Message.query.filter_by(receiver_id=current_user.id).all()
    return render_template("received.html", received_messages=received_messages)


@app.route("/sent", methods=["GET"])
@login_required
def sent():
    sent_messages = Message.query.filter_by(sender_id=current_user.id)
    return render_template("sent.html", sent_messages=sent_messages)


@app.route("/message/<message_id>", methods=["GET"])
@login_required
def message(message_id):
    message = Message.query.filter_by(id=int(message_id)).first()
    return render_template("message.html", message=message)


@app.route("/message/<message_id>/delete", methods=["GET"])
@login_required
def message_delete(message_id):
    message = Message.query.filter_by(id=message_id).first()
    if current_user.id == message.receiver_id:
        db.session.delete(message)
        db.session.commit()

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
@login_required
def profile_delete():
    user = User.query.filter_by(id=current_user.id).first()
    if request.method == "POST":
        db.session.delete(user)
        db.session.commit()
        flash("Your profile has been deleted")
        return redirect(url_for("index"))
    return render_template("profile_delete.html")



@app.before_request
def before_request():
    """Update user's last_seen attribute on every request made."""
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


