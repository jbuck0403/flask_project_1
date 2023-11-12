from flask import request, render_template, redirect, url_for, flash
import requests, random
from app import app
from app.forms import PokedexInputForm, LoginForm, SignupForm, AccountForm
from app.models import User, db
from flask_login import logout_user, current_user, login_required
from app.Pokedex import Pokedex

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
        print(user)

        db.session.add(user)
        db.session.commit()
        
        flash("Account created!", "success")
        return redirect(url_for('login'))
    
    return render_template('signup.jinja', form=form)

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = AccountForm()
    if request.method == "POST":
        if "logoutBtn" in request.form:
            logout_user()
            flash("Logged out...", "warning")
            return redirect(url_for('login'))

    return render_template('account.jinja', form=form)


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

        return pokedex.render_pokedex(pokemonInfoDict=pokemonInfoDict.items(), spriteURL=spriteURL, spriteShinyURL=spriteShinyURL)
        
    
    return pokedex.render_pokedex()