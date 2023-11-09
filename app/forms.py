from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from app.users import REGISTERED_USERS

class PokedexInputForm(FlaskForm):
    pokedexInput = StringField('Enter Pokémon', validators=[DataRequired()])


class LoginForm(FlaskForm):
    userName = StringField("User Name:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    loginBtn = SubmitField("Sign In")
    signupBtn = SubmitField("Create Account")

def verifyUniqueUserName(_, userName):
    if userName.data in REGISTERED_USERS.keys():
        raise ValidationError('User Name not available...')

def verifyPasswordRequirements(_, password):
    minimumLength = 6
    if len(password.data) < minimumLength:
        raise ValidationError(f'Password must be at least {minimumLength} characters long...')

class SignupForm(FlaskForm):
    userName = StringField("User Name:", validators=[DataRequired(), verifyUniqueUserName])
    password = PasswordField("Password:", validators=[DataRequired(), verifyPasswordRequirements])
    confirmPassword = PasswordField("Confirm Password:", validators=[DataRequired(), EqualTo('password', message="Passwords must match...")])
    createAccountBtn = SubmitField("Create Account")
