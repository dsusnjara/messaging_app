import os
from sqla_wrapper import SQLAlchemy

db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///localhost.sqlite"))


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    session_token = db.Column(db.String)

    messages_sent = db.relationship("Message",
                                    foreign_keys="Message.sender_id",
                                    backref="sender",
                                    lazy=True
                                    )

    messages_received = db.relationship("Message",
                                        foreign_keys="Message.receiver_id",
                                        backref="receiver",
                                        lazy=True
                                        )


class Message(db.Model):
    __tablename__ = "message"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    message = db.Column(db.Text)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"))
