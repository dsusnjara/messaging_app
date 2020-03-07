from flask_wtf import FlaskForm
from app.models import  User
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError("Please use different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError("Please use different email address.")


class EditProfileForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    about_me = TextAreaField("About me", validators=[Length(min=0, max=140)])
    submit = SubmitField("Submit")


class MessageForm(FlaskForm):
    title = TextAreaField("Title", validators=[DataRequired(message="Message has to have a title")])
    body = TextAreaField("Message", validators=[DataRequired(message="Please don't send empty messages!")])
    send_to = StringField("Send To", validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate_send_to(self, send_to):
        user = User.query.filter_by(username=send_to.data).first()
        #//TODO: uppercase and lowercase insesitivity
        if user is None:
            raise ValidationError("That user does not exist")