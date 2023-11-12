from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User, db
from flask_login import login_user, current_user
import re

def verifyAllowedInput(_, userInput):
    pattern = re.compile(r'^[\-a-zA-Z0-9]*$')
    if not pattern.match(userInput.data):
        raise ValidationError("Only letters and numbers...")

def verifyUniqueUserName(_, userName):
    queriedUser = User.query.filter(User.userName == userName.data).first()

    if queriedUser:
        raise ValidationError('User Name not available...')

def verifyPasswordRequirements(_, password):
    minimumLength = 6
    if len(password.data) < minimumLength:
        raise ValidationError(f'Password must be at least {minimumLength} characters long...')

def verifyUserNameRequirements(_, userName):
    verifyAllowedInput(_, userName)
    verifyUniqueUserName(_, userName)    

def notEmpty(_, userInput):
    if userInput.data == None or len(userInput.data.strip()) == 0:
        
        raise ValidationError(f"{str(userInput.label)} cannot be blank...")

def verifyPassword(_, currentPassword):
    currentUserPassword = User.query.filter(User.userName == current_user.userName).first().password
    
    if not check_password_hash(currentUserPassword, currentPassword.data):
        raise ValidationError('Invalid password...')

class PokedexInputForm(FlaskForm):
    pokedexInput = StringField('Enter Pokémon', validators=[notEmpty, verifyAllowedInput])

class LoginForm(FlaskForm):
    userName = StringField("User Name", validators=[notEmpty])
    password = PasswordField("Password", validators=[notEmpty])
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

class SignupForm(FlaskForm):
    userName = StringField("User Name", validators=[notEmpty, verifyUserNameRequirements])
    password = PasswordField("Password", validators=[verifyPasswordRequirements])
    confirmPassword = PasswordField("Confirm Password", validators=[EqualTo('password', message="Passwords must match...")])
    createAccountBtn = SubmitField("Create Account")

class AccountForm(FlaskForm):
    logoutBtn = SubmitField("Logout")
    cancelBtn = SubmitField("Cancel")
    changePasswordBtn = SubmitField("Change Password")
    changeUserNameBtn = SubmitField("Change Name")

class UpdateAccountUserNameForm(AccountForm):
    changeUserName = StringField("New User Name", validators=[notEmpty, verifyUserNameRequirements])
    password = PasswordField("Password", validators=[notEmpty, verifyPassword])

    def updateUserName(self):
        try:
            current_user.userName = self.changeUserName.data
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False
        
class UpdateAccountPasswordForm(AccountForm):
    newPassword = PasswordField("New Password", validators=[verifyPasswordRequirements])
    confirmNewPassword = PasswordField("Confirm New Password", validators=[EqualTo('newPassword', message="Passwords must match...")])
    currentPassword = PasswordField("Current Password", validators=[notEmpty, verifyPassword])

    def updatePassword(self):
        try:
            current_user.password = generate_password_hash(self.newPassword.data)
            db.session.commit()
            return True
        except:
            db.session.rollback()
            return False