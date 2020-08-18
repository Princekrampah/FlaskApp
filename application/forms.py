from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from application.models import Users
from wtforms.validators import InputRequired, EqualTo, ValidationError, Length, Email
from wtforms import StringField, PasswordField, SubmitField, IntegerField, TextAreaField


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    Class = StringField("Class", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = Users.query.filter_by(username = username.data).first()
        if user:
            raise ValidationError("That username is already taken please choose a different one.")

    def validate_email(self, email):
        user = Users.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError("That email is already in use, choose a different one.")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class TeacherPostForm(FlaskForm):
    title = StringField("Post Title", validators=[InputRequired(), Length(max =60)])
    instructions = TextAreaField("Instructions", validators=[InputRequired(), Length(max=100)])
    Class = StringField("Target class", validators=[InputRequired()])
    content_file = FileField("chooce file", validators=[FileRequired(), FileAllowed(["pdf"])])
    submit = SubmitField("Post")


class StudentQuestionForm(FlaskForm):
    content = TextAreaField("Content", validators=[InputRequired()])
    submit = SubmitField("Submit")