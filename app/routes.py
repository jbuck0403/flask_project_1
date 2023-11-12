from flask import request, render_template, redirect, url_for, flash, session
import requests, random
from app import app
from app.forms import PokedexInputForm, LoginForm, SignupForm, AccountForm, UpdateAccountUserNameForm, UpdateAccountPasswordForm, DeleteAccountForm
from app.models import User, db
from flask_login import logout_user, current_user, login_required
from app.Pokedex import Pokedex

@app.context_processor
def injectFavoriteSprite():
    if current_user.is_authenticated and current_user.favoritePkmn != None:
        pokedex = Pokedex()
        favoritePkmn = current_user.favoritePkmn.split(',')
        pkmnID, spriteType = favoritePkmn[0], False if favoritePkmn[1] == 'd' else True

        favoriteSprite = pokedex.returnSpriteURL(pkmn=pkmnID, pkmnType='pokemon', shiny=spriteType)
    else:
        favoriteSprite = None
    return dict(favoriteSprite=favoriteSprite)

@app.route("/", methods=['GET', 'POST'])
def landingPage():
    pokedex = Pokedex()

    return render_template('landingPage.jinja', unownWord=pokedex.unownSpeller("welcome"))
    
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
            return app.login_manager.unauthorized()

    form = LoginForm()

    if request.method == "POST":
        if "loginBtn" in request.form and form.validate_on_submit() and form.attemptLogin():
            flash("Successfully logged in!", "success")
            return redirect (url_for("landingPage"))
        elif "signupBtn" in request.form:
            return redirect(url_for("signup"))
        
    return render_template('login.jinja', form=form)

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
            return app.login_manager.unauthorized()

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
        
        return redirect(url_for('login'))
    
    return render_template('signup.jinja', form=form)

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    def render_account(**kwargs):
        return render_template('account.jinja', **kwargs)

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
            return redirect(url_for('login'))
        
        elif "cancel" in request.form:
            return render_account(form=form)
        
        elif "changeUserName" in request.form:
            if userNameForm.validate_on_submit():
                if not userNameForm.updateUserName():
                    flash("Error updating User Name...", "error")
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
                return render_account(form=passwordForm, requestPasswordChange=True)
            
        elif "changePasswordBtn" in request.form:
            return render_account(form=passwordForm, requestPasswordChange=True)
        
        elif "verifyIntentionToDelete" in request.form:
            if deleteAccountForm.validate_on_submit():
                if not deleteAccountForm.deleteAccount():
                    flash("Error deleting account...", "error")
                else:
                    return redirect(url_for("landingPage"))
            else:
                return render_account(form=deleteAccountForm, requestDeleteAccount=True)

        elif "deleteAccountBtn" in request.form:
            return render_account(form=deleteAccountForm, requestDeleteAccount=True)
    
    return render_account(form=form)


@app.route("/pokedex", methods=['GET', 'POST'])
def pokedex():
    form = PokedexInputForm()
    pokedex = Pokedex(form)

    if request.method == "POST" and form.validate_on_submit():

        pokemonData = pokedex.returnPokemonData(form)

        if isinstance(pokemonData, int):
            return pokedex.renderSprite(pokemonData, unownWord=True)
        else:
            pokemonInfoDict, spriteURL, spriteShinyURL = pokemonData

        if spriteURL != None:
            spriteResponse = requests.get(spriteURL)
        if spriteShinyURL != None:
            shinySpriteResponse = requests.get(spriteShinyURL)

        if  spriteURL == None or not spriteResponse.ok:
            return pokedex.render_pokedex(pokemonInfoDict=pokemonInfoDict.items())
        if  spriteShinyURL == None or not shinySpriteResponse.ok:
            return pokedex.render_pokedex(pokemonInfoDict=pokemonInfoDict.items(), spriteURL=spriteURL)

        print(spriteURL)
        return pokedex.render_pokedex(pokemonInfoDict=pokemonInfoDict.items(), spriteURL=spriteURL, spriteShinyURL=spriteShinyURL)
        
    
    return pokedex.render_pokedex()

@app.route("/favorite", methods=['GET', 'POST'])
@login_required
def favorite():
    form = PokedexInputForm()
    pokedex = Pokedex(form)

    if request.method == "POST":
        print(request.form)
        if "favoritePkmn" in request.form or "favoriteShinyPkmn" in request.form:
            pokedexID = session.pop('pokedexID', current_user.userName)
            shiny = False
            if "favoriteShinyPkmn" in request.form:
                shiny = True

            try:
                current_user.favoritePkmn = f"{pokedexID},{'s' if shiny else 'd'}"
                db.session.commit()
                flash("Favorite successfully assigned!", "success")
            except:
                db.session.rollback()
                flash("Error assigning favorite...", "error")

        elif "pokedexInput" in request.form and form.validate_on_submit():
            pokemonData = pokedex.returnPokemonData(form, favorite=True)
            if not isinstance(pokemonData, int):
                name, pokedexID, sprite, shinySprite = pokemonData
            else:
                sprite = pokemonData
            form.pokedexInput.data = ""
            if isinstance(sprite, int):
                unownWord = pokedex.unownSpeller()
                if isinstance(unownWord[0], int):
                    return render_template("favorite.jinja", form=form, errorCode=unownWord[0])
                return render_template("favorite.jinja", form=form, unownWord=unownWord)
            
            session['pokedexID'] = pokedexID
            
            return render_template("favorite.jinja", form=form, spriteURL=sprite, shinySpriteURL=shinySprite, name=name)

    return render_template("favorite.jinja", form=form)