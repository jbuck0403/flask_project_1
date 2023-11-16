from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import User, db
from flask_login import login_user, current_user
from app.validators import notEmpty, verifyUserNameRequirements, verifyPasswordRequirements, verifyPassword, DELETE_ACCOUNT_KEYWORD, verifyDifferentUserName, verifyDifferentPassword

class LoginForm(FlaskForm):
    userName = StringField("User Name", validators=[notEmpty])
    password = PasswordField("Password", validators=[notEmpty])
    loginBtn = SubmitField("Log In")
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
    deleteAccountBtn = SubmitField("Delete Account")
    confirmLogoutBtn = SubmitField("Confirm Logout")

class UpdateAccountUserNameForm(AccountForm):
    changeUserName = StringField("New User Name", validators=[notEmpty, verifyDifferentUserName, verifyUserNameRequirements])
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
    newPassword = PasswordField("New Password", validators=[verifyPasswordRequirements, verifyDifferentPassword])
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
        
def confirmDeleteAccount(_, userInput):
    if userInput.data != DELETE_ACCOUNT_KEYWORD:
        raise ValidationError("Enter the exact word...")
    
def confirmAccountExists(_, userInput):
    queriedUser = User.query.filter(User.userName == userInput.data).first()

    if not queriedUser:
        raise ValidationError("Invalid User Name...")
    
def confirmUserLoggedIn(_, userInput):
    if not current_user.userName == userInput.data:
        raise ValidationError("Cannot delete account that isn't logged in...")

class DeleteAccountForm(AccountForm):
    verifyIntentionToDelete = StringField(f"Type '{DELETE_ACCOUNT_KEYWORD}'", validators=[confirmDeleteAccount])
    userName = StringField("User Name", validators=[notEmpty, confirmAccountExists, confirmUserLoggedIn])
    password = PasswordField("Password", validators=[notEmpty, verifyPassword])

    def deleteAccount(self):
        queriedUser = User.query.filter(User.userName == self.userName.data).first()
        print(queriedUser)
        
        if current_user.userName == queriedUser.userName:
            try:
                user = db.session.query(User).get(current_user.id)
                db.session.delete(user)
                db.session.commit()
                return True
            except:
                db.session.rollback()
                return False