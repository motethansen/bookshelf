from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextField, HiddenField, DateTimeField, validators, IntegerField, SubmitField
from wtforms.validators import DataRequired



class LoginForm(FlaskForm):
    """Login form to access writing and settings pages"""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name  = StringField('first_name', validators=[DataRequired()])
    last_name   = StringField('last_name', validators=[DataRequired()])
    email       = StringField('email', validators=[DataRequired()])
    password    = PasswordField('New Password', validators=[DataRequired()])
    confirm     = PasswordField('Repeat Password', validators=[DataRequired()])
