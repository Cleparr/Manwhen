#Auth routes for the app

from click import echo
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import Manga, MangaChapter, User


auth = Blueprint('auth', __name__)

   
@auth.route("/login", methods=['GET'])
def login():

    return render_template('login.html')

@auth.route("/login", methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Votre mot de passe ou adresse mail est invalide.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    
    return redirect(url_for('main.home'))



@auth.route("/signup", methods=['GET'])
def signup():

    return render_template('signup.html')


@auth.route("/signup", methods=['POST'])
def signup_post():

    email = request.form['email']
    password = request.form['password']

    echo(email)
    echo(password)

    user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Cette adresse mail existe déjà')
        return redirect(url_for('auth.signup')) 
    
    new_user = User(email=email, password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
