from enum import auto
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import login_required, current_user, fresh_login_required, logout_user
from .models import User, Post
from . import confirmed_required, db, valid_type, custom_filename, valid_username, send_delete_email

profile = Blueprint('profile', __name__)

@profile.route('/<username>', methods=['GET', 'POST'])
def prof(username):
  page = request.args.get('page', 1, type=int)

  user = User.query.filter_by(username=username).first_or_404()
  posts = Post.query.filter_by(author=user).order_by(Post.created.desc())\
    .paginate(page, current_app.config["POSTS_PER_PAGE"], True)

  return render_template("profile.html", author=user, posts=posts)

@profile.route('/<username>/settings', methods=['GET', 'POST'])
@fresh_login_required
@confirmed_required
def settings(username):
  user = User.query.filter_by(username=username).first_or_404()

  if user != current_user:
    abort(403)
  
  if request.method == 'POST':
    username = request.form.get("username")
    description = request.form.get("description")
    firstName = request.form.get("firstName")
    lastName = request.form.get("lastName")

    if not description:
      description = "No description..."

    if not valid_username(username, user.id):
      flash('Username already exists.', category='error')
    elif len(username) < 4:
      flash('Username must be greater than 3 characters.', category='error')
    elif len(firstName) < 2:
      flash('First Name must be greater than 1 characters.', category='error')
    elif len(lastName) < 2:
      flash('Last Name must be greater than 1 characters.', category='error')
    else:
      user.username = username
      user.description = description
      user.first_name = firstName
      user.last_name = lastName

      if request.form.get("activate-pwd") == "on":
        if request.form.get("password1") != request.form.get("password2"):
          flash('Passwords don\'t match. Password couldn\'t be updated.', category='error')
        elif len(request.form.get("password1")) < 8:
          flash('Password must be greater than 7 characters. Password couldn\'t be updated.', category='error')
        else:
          user.password = request.form.get("password1")
      
      f = request.files['profilePic']
      if f.filename:
        if not valid_type(f.filename):
          flash(f"'{f.filename}' is not a valid filetype. Only .png, .jpg and .jpeg are accepted.")
        else:
          filename = custom_filename(f.filename)
          f.save(current_app.config['PROFILE_PICTURE_FOLDER'] + filename)
          user.profile_pic = filename
    
      db.session.commit()
      flash('Data updated successfully!', category='success')
      return redirect(url_for("profile.prof", username=user.username))

  return render_template("settings.html", author=current_user)

@profile.route("/<username>/followers")
def followers(username):
  page = request.args.get('page', 1, type=int)

  user = User.query.filter_by(username=username).first_or_404()
  followers = user.followers.paginate(page, current_app.config["POSTS_PER_PAGE"], True)

  return render_template("followers.html", followers=followers, author=user)

@profile.route("/<username>/following")
def following(username):
  page = request.args.get('page', 1, type=int)

  user = User.query.filter_by(username=username).first_or_404()
  following = user.followed.paginate(page, current_app.config["POSTS_PER_PAGE"], True)

  return render_template("following.html", following=following, author=user)

@profile.route("/<username>/follow", methods=["POST"])
@login_required
@confirmed_required
def follow(username):
  user = User.query.filter_by(username=username).first_or_404()

  if user != current_user:
    abort(403)

  target = User.query.filter_by(username=request.form.get("target")).first_or_404()

  if not user.is_following(target):
    if target != user:
      user.follow(target)
      flash(f" You are following {target.username}", category="success")
    else:
      flash("You cannot follow yourself!", category="error")
  else:
    if target != user:
      user.unfollow(target)
      flash(f" You are not following {target.username}", category="success")
    else:
      flash("You cannot unfollow yourself!", category="error")
  
  db.session.commit()
  return redirect(url_for("profile.prof", username=target.username))


@profile.route('/<username>/delete-account')
@login_required
@confirmed_required
def deleteacc(username):
  user = User.query.filter_by(username=username).first_or_404()
  
  if user != current_user:
    abort(403)

  send_delete_email(user)
  flash('An email has been sent with instructions to delete your account.', category='success')

  return redirect(url_for("profile.prof", username=user.username))


@profile.route('/<username>/delete-account/<token>', methods=['GET', 'POST'])
@login_required
@confirmed_required
def delete_confirm(username, token):
  _user = User.query.filter_by(username=username).first_or_404()
  user, command = User.verify_token(token)
  if user is None or command != 'delete-account':
    flash('That is an expired or invalid token.', category='error')
    return redirect(url_for('profile.delete-account', username=_user.username))
  
  if user != current_user or user != _user:
    abort(403)

  if request.method == "POST":
    delete = request.form.get('yes')
    if delete is None:
      return redirect(url_for("profile.prof", username=user.username))
    
    logout_user()
    for p in Post.query.filter_by(author=user).all():
      db.session.delete(p)
    db.session.delete(user)
    db.session.commit()
    flash('Account deleted successfully!', category='success')
    return redirect(url_for('home.index'))

  return render_template("deleteacc.html", author=user)
