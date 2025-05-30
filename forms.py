from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, IntegerField, SubmitField, FileField, DateTimeField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
from flask_wtf.file import FileAllowed

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class TeamForm(FlaskForm):
    name = StringField('Team Name', validators=[DataRequired(), Length(max=100)])
    coach = StringField('Coach', validators=[DataRequired(), Length(max=100)])
    founded_year = IntegerField('Founded Year', validators=[DataRequired(), NumberRange(min=1800, max=2025)])
    logo = FileField('Team Logo', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Save')

class PlayerForm(FlaskForm):
    name = StringField('Player Name', validators=[DataRequired(), Length(max=100)])
    position = StringField('Position', validators=[DataRequired(), Length(max=50)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=15, max=50)])
    photo = FileField('Photo', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    submit = SubmitField('Save')

class MatchForm(FlaskForm):
    team1_id = SelectField('Team 1', coerce=int, validators=[DataRequired()])
    team2_id = SelectField('Team 2', coerce=int, validators=[DataRequired()])
    score = StringField('Score', validators=[Length(max=10)])
    date = DateTimeField('Match Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Save')

class SearchForm(FlaskForm):
    query = StringField('Search', validators=[DataRequired()])
    submit = SubmitField('Search')

class UserManagementForm(FlaskForm):
    role = SelectField('Role', choices=[('User', 'User'), ('Admin', 'Admin')], validators=[DataRequired()])
    is_blocked = BooleanField('Block User')
    submit = SubmitField('Update')