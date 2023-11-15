from wtforms.validators import ValidationError
from werkzeug.security import check_password_hash
from app.models import User
from flask_login import current_user
import re

DELETE_ACCOUNT_KEYWORD = "DELETE"

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
    
def verifyDifferentUserName(_, userInput):
    if userInput.data == current_user.userName:
        raise ValidationError('Must be different from current User Name...')
    
def verifyDifferentPassword(_, userInput):
    if check_password_hash(current_user.password, userInput.data):
        raise ValidationError('Must be different from current password...')