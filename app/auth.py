from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user, logout_user, login_user
from .models import User, Post
from . import db
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated:
    flash('You are already logged in.', category='error')
    return redirect(url_for('home.index'))

  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user:
      if check_password_hash(user.password, password):
        login_user(user)
        flash('Logged in successfully!', category='success')
        return redirect(url_for("profile.prof", username=user.username))
      else:
        flash('Incorrect Username or Password.', category='error')
    else:
      flash('Incorrect Username or Password.', category='error')

  return render_template("login.html", user=current_user)


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
  if current_user.is_authenticated:
    flash('You are already logged in.', category='error')
    return redirect(url_for('home.index'))

  if request.method == 'POST':
    email = request.form.get('email')
    username = request.form.get('username')
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    user1 = User.query.filter_by(email=email).first()
    user2 = User.query.filter_by(username=username).first()
    if user1:
      flash('Email already exists.', category='error')
    elif user2:
      flash('Username already exists.', category='error')
    elif len(email) < 4:
      flash('Email must be greater than 3 characters.', category='error')
    elif len(username) < 4:
      flash('Username must be greater than 3 characters.', category='error')
    elif len(firstName) < 2:
      flash('First Name must be greater than 1 characters.', category='error')
    elif len(lastName) < 2:
      flash('Last Name must be greater than 1 characters.', category='error')
    elif password1 != password2:
      flash('Passwords don\'t match.', category='error')
    elif len(password1) < 8:
      flash('Password must be greater than 7 characters.', category='error')
    else:
      new_user = User(email=email, username=username, first_name=firstName, last_name=lastName, password=generate_password_hash(password1, method='sha512'))
      db.session.add(new_user)
      db.session.commit()
      flash('Account created!', category='success')
      login_user(new_user, remember=True)
      return redirect(url_for("profile.prof", username=new_user.username))


  return render_template('signup.html', user=current_user)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
  logout_user()
  flash('Logged out successfully!', category='success')
  return redirect(url_for('home.index'))