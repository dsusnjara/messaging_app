from flask import Flask, render_template, request, make_response, redirect, url_for
from models import db, User, Message
import hashlib
import uuid

app = Flask(__name__)
db.create_all()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


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

        response = make_response(redirect(url_for("send")))
        response.set_cookie("session_token", session_token, httponly=True, samesite="Strict")

        return response

    return render_template("login.html")


@app.route("/send")
def send():
    name = User.name
    users = db.query(User).filter_by(name=name).all()
    return render_template("send.html", users=users)


@app.route("/received")
def received():
    return render_template("received.html")


@app.route("/sent")
def sent():
    return render_template("sent.html")


if __name__ == "__main__":
    app.run(debug=True)
