from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user, logout_user, login_user
from .models import User, Post
from . import db, valid_username, mail
from flask_mail import Message
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
  if current_user.is_authenticated and not request.args.get("reauth"):
    flash('You are already logged in.', category='error')
    return redirect(url_for('home.index'))

  if request.method == 'POST':
    username = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(username=username).first()
    if user and user.verify_password(password):
      login_user(user, remember=True)
      flash('Logged in successfully!', category='success')

      next = request.args.get('next')

      return redirect(next or url_for("profile.prof", username=user.username))
    else:
      flash('Incorrect Username or Password.', category='error')
    
  return render_template("login.html")


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
  if current_user.is_authenticated:
    flash('You are already logged in.', category='error')
    return redirect(url_for('home.index'))

  if request.method == 'POST':
    email = request.form.get('email')
    username = request.form.get('username')
    description = request.form.get('description')
    firstName = request.form.get('firstName')
    lastName = request.form.get('lastName')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    if not description:
      description = "No description..."

    user1 = User.query.filter_by(email=email).first()
    if user1:
      flash('Email already exists.', category='error')
    elif not valid_username(username):
      flash('Username already exists.', category='error')
    elif len(email) < 4:
      flash('Email must be longer than 3 characters.', category='error')
    elif len(username) < 4:
      flash('Username must be longer than 3 characters.', category='error')
    elif len(firstName) < 2:
      flash('First Name must be longer than 1 characters.', category='error')
    elif len(lastName) < 2:
      flash('Last Name must be longer than 1 characters.', category='error')
    elif password1 != password2:
      flash('Passwords don\'t match.', category='error')
    elif len(password1) < 8:
      flash('Password must be longer than 7 characters.', category='error')
    else:
      new_user = User(email=email, username=username, description=description, first_name=firstName, last_name=lastName, password=password1)
      db.session.add(new_user)
      db.session.commit()
      flash('Account created!', category='success')
      login_user(new_user, remember=True)
      return redirect(url_for("profile.prof", username=new_user.username))


  return render_template('signup.html')


@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
  logout_user()
  flash('Logged out successfully!', category='success')
  return redirect(url_for('home.index'))

def send_reset_email(user):
  if not user:
    return
  
  token = user.get_token(command="reset-password")
  
  msg = Message("Password Reset Request", sender="noreply@blogopedia.com", recipients=[user.email])
  msg.body = f"""To reset your password, please visit the following link:
{ url_for('auth.reset_token', token=token, _external=True) }

If you did not make this request then simply ignore this email and no changes will be made."""

  mail.send(msg)

@auth.route('/reset-password', methods=['GET', 'POST'])
def reset_request():
  if current_user.is_authenticated:
    flash('You are already logged in.', category='error')
    return redirect(url_for('home.index'))

  if request.method == 'POST':
    email = request.form.get('email')
    user = User.query.filter_by(email=email).first()
    send_reset_email(user)
    flash('An email has been sent with instructions to reset your password.', category='success')
    return redirect(url_for('auth.login'))

  return render_template("reset_password.html")

@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_token(token):
  if current_user.is_authenticated:
    flash('You are already logged in.', category='error')
    return redirect(url_for('home.index'))

  user, command = User.verify_token(token)
  if user is None or command != 'reset-password':
    flash('That is an expired or invalid token.', category='error')
    return redirect(url_for('auth.reset_request'))
  
  if request.method == 'POST':
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')

    if password1 != password2:
      flash('Passwords don\'t match.', category='error')
    elif len(password1) < 8:
      flash('Password must be longer than 7 characters.', category='error')
    else:
      user.password = password1
      db.session.commit()
      flash('Your password has been updated! Your are now able to log in.', category='success')
      return redirect(url_for("auth.login"))
  
  return render_template('reset_token.html')