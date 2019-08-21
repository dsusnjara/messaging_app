from flask import Flask, render_template, request, make_response, redirect, url_for
from models import db, User, Message
import requests
from os import urandom
import hashlib
import uuid

app = Flask(__name__)
db.create_all()
app.secret_key = urandom(24)


@app.route("/", methods=["GET"])
def index():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    query = "Zagreb"
    unit = "metric"
    api_key = ""

    url = "https://api.openweathermap.org/data/2.5/weather?q={0}&units={1}&appid={2}".format(query, unit, api_key)
    data = requests.get(url=url)
    return render_template("index.html", user=user, data=data.json())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("user-name")
        email = request.form.get("user-email")
        password = request.form.get("user-password")

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = User(name=name, email=email, password=hashed_password)

        db.add(user)
        db.commit()

        return make_response(redirect(url_for("login")))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("user-name")
        password = request.form.get("user-password")

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        user = db.query(User).filter_by(name=name).first()

        if not user or hashed_password != user.password:
            error_message = "Wrong username or password! Try again!"
            return render_template("login.html", message=error_message)

        elif hashed_password == user.password:
            session_token = str(uuid.uuid4())
            user.session_token = session_token

            db.add(user)
            db.commit()

        response = make_response(redirect(url_for("index")))
        response.set_cookie("session_token", user.session_token, httponly=True, samesite="Strict")

        return response

    return render_template("login.html")


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


@app.route("/received", methods=["GET", "POST"])
def received():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    user_id = user.id
    received_messages = db.query(Message).filter_by(receiver_id=user_id).all()
    message1 = db.query(Message).filter_by(receiver_id=user_id).first()

    if request.method == "POST":
        db.delete(message1)
        db.commit()
        return redirect(url_for("received"))

    return render_template("received.html", received_messages=received_messages, user=user)


@app.route("/sent", methods=["GET", "POST"])
def sent():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    user_id = user.id
    sent_messages = db.query(Message).filter_by(sender_id=user_id).all()
    message1 = db.query(Message).filter_by(sender_id=user_id).first()

    if request.method == "POST":
        db.delete(message1)
        db.commit()
        return redirect(url_for("sent"))

    return render_template("sent.html", sent_messages=sent_messages, user=user)


@app.route("/message/<message_id>", methods=["GET"])
def message(message_id):
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    message = db.query(Message).get(int(message_id))
    return render_template("message.html", message=message, user=user)


@app.route("/profile", methods=["GET"])
def profile():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()
    name = User.name
    users = db.query(User).filter_by(name=name).all()
    return render_template("profile.html", user=user, users=users)


@app.route("/profile/edit", methods=["GET", "POST"])
def profile_edit():
    session_token = request.cookies.get("session_token")
    user = db.query(User).filter_by(session_token=session_token).first()

    if request.method == "GET":
        return render_template("profile_edit.html", user=user)

    elif request.method == "POST":
        name = request.form.get("profile-name")
        email = request.form.get("profile-email")
        old_password = request.form.get("old-password")
        new_password = request.form.get("new-password")

        if old_password and new_password:
            hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()

            if hashed_old_password == user.password:
                user.password = hashed_new_password
                db.add(user)
                db.commit()
                info = "Password successfully changed!"
                return render_template("profile_edit.html", info=info, user=user)

            else:
                info = "Wrong password! Try again!"
                return render_template("profile_edit.html", info=info, user=user)

        user.name = name
        user.email = email

        db.add(user)
        db.commit()

        return redirect(url_for("profile"))


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


@app.route("/logout")
def logout():
    response = make_response(redirect(url_for("index")))
    response.set_cookie("session_token", expires=0)
    return response


if __name__ == "__main__":
    app.run(debug=True)
