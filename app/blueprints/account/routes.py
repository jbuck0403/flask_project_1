from flask import request, render_template, redirect, url_for, flash
from app.models import User, db
from flask_login import logout_user, current_user, login_required
from .forms import (
    LoginForm,
    SignupForm,
    AccountForm,
    UpdateAccountUserNameForm,
    UpdateAccountPasswordForm,
    DeleteAccountForm,
)
from . import account


@account.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return account.login_manager.unauthorized()

    form = LoginForm()

    if request.method == "POST":
        if (
            "loginBtn" in request.form
            and form.validate_on_submit()
            and form.attemptLogin()
        ):
            flash("Successfully logged in!", "success")
            return redirect(url_for("main.landingPage"))
        elif "signupBtn" in request.form:
            return redirect(url_for("account.signup"))

    return render_template("login.jinja", form=form)


@account.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return account.login_manager.unauthorized()

    form = SignupForm()

    if request.method == "POST" and form.validate_on_submit():
        userName = form.userName.data
        password = form.password.data

        user = User(userName, password)

        try:
            db.session.add(user)
            db.session.commit()
            flash("Account created!", "success")
        except:
            db.session.rollback()
            flash("Error creating account...", "error")

        return redirect(url_for("account.login"))

    return render_template("signup.jinja", form=form)


@account.route("/account", methods=["GET", "POST"])
@login_required
def account():
    def render_account(**kwargs):
        return render_template("account.jinja", **kwargs)

    form = AccountForm()
    userNameForm = UpdateAccountUserNameForm()
    passwordForm = UpdateAccountPasswordForm()
    deleteAccountForm = DeleteAccountForm()

    if request.method == "POST":
        if "logoutBtn" in request.form:
            return render_account(form=form, requestConfirmLogout=True)

        if "confirmLogoutBtn" in request.form:
            logout_user()
            flash("Logged out...", "warning")
            return redirect(url_for("account.login"))

        elif "cancel" in request.form:
            return render_account(form=form)

        elif "changeUserName" in request.form:
            if userNameForm.validate_on_submit():
                if not userNameForm.updateUserName():
                    flash("Error updating User Name...", "error")
                else:
                    flash("User Name changed successfully!", "success")
            else:
                userNameForm.changeUserName.data = ""
                return render_account(form=userNameForm, requestUserNameChange=True)

        elif "changeUserNameBtn" in request.form:
            return render_account(form=userNameForm, requestUserNameChange=True)

        elif "currentPassword" in request.form:
            if passwordForm.validate_on_submit():
                if not passwordForm.updatePassword():
                    flash("Error updating password...", "error")
                else:
                    flash("Password changed successfully!", "success")
            else:
                return render_account(form=passwordForm, requestPasswordChange=True)

        elif "changePasswordBtn" in request.form:
            return render_account(form=passwordForm, requestPasswordChange=True)

        elif "verifyIntentionToDelete" in request.form:
            if deleteAccountForm.validate_on_submit():
                if not deleteAccountForm.deleteAccount():
                    flash("Error deleting account...", "error")
                else:
                    flash("Account deleted successfully.", "success")
                    return redirect(url_for("main.landingPage"))
            else:
                return render_account(form=deleteAccountForm, requestDeleteAccount=True)

        elif "deleteAccountBtn" in request.form:
            return render_account(form=deleteAccountForm, requestDeleteAccount=True)

    return render_account(form=form)
