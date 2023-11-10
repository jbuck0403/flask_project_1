from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from werkzeug.security import check_password_hash
from app.models import User
from flask_login import login_user
import re

def verifyAllowedInput(_, userInput):
    pattern = re.compile(r'^[\-a-zA-Z0-9]+$')
    if not pattern.match(userInput.data):
        raise ValidationError("Only letters and numbers...")

class PokedexInputForm(FlaskForm):
    pokedexInput = StringField('Enter Pokémon', validators=[DataRequired(), verifyAllowedInput])

class LoginForm(FlaskForm):
    userName = StringField("User Name:", validators=[DataRequired()])
    password = PasswordField("Password:", validators=[DataRequired()])
    loginBtn = SubmitField("Sign In")
    signupBtn = SubmitField("Create Account")

    def attemptLogin(self):
        queriedUser = User.query.filter(User.userName == self.userName.data).first()

        if not queriedUser:
            self.userName.errors.append('Invalid User Name...')
            return False
        
        if not check_password_hash(queriedUser.password, self.password.data):
            self.password.errors.append('Invalid password...')
            return False
        else:
            login_user(queriedUser)
            return True

def verifyUniqueUserName(_, userName):
    queriedUser = User.query.filter(User.userName == userName.data).first()

    if queriedUser:
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

class AccountForm(FlaskForm):
    logout = SubmitField("Logout")
