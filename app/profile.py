from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, abort
from flask_login import login_required, current_user, fresh_login_required
from .models import User, Post
from . import db, valid_type, custom_filename, valid_username, valid_title
import json

profile = Blueprint('profile', __name__)

@profile.route('/<username>', methods=['GET', 'POST'])
def prof(username):
  user = User.query.filter_by(username=username).first_or_404()

  return render_template("profile.html", author=user)

@profile.route('/<username>/settings', methods=['GET', 'POST'])
@fresh_login_required
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
          f.save(filename)
          user.profile_pic = filename
    
      db.session.commit()
      flash('Data updated successfully!', category='success')
      return redirect(url_for("profile.prof", username=user.username))

  return render_template("settings.html", author=current_user)

@profile.route('/<username>/delete-account')
@login_required
def deleteacc(username):
  user = User.query.filter_by(username=username).first_or_404()
  
  if user != current_user:
    abort(403)

  if request.method == 'POST':
    pass

  return render_template("deleteacc.html", author=current_user)

@profile.route('/<username>/<title>')
def post(username, title):
  user = User.query.filter_by(username=username).first_or_404()
  post = Post.query.filter_by(title=title, author=user).first_or_404()

  return render_template("post.html",  author=user, post=post)

@profile.route('/<username>/create', methods=["GET", "POST"])
@login_required
def create(username):
  user = User.query.filter_by(username=username).first_or_404()
  
  if user != current_user:
    abort(403)
  
  if request.method == 'POST':
    title = request.form.get('title')
    description = request.form.get('description')
    data = request.form.get('data')

    if not description:
      description = "No description..."

    if not valid_title(title):
      flash('Title already exists.', category='error')
    elif len(description) < 4:
      flash('Description must be longer than 3 characters.', category='error')
    elif len(data) < 10:
      flash('Content must be longer than 10 characters.', category='error')
    else:
      new_post = Post(title=title, description=description, content=data, author=user)
      db.session.add(new_post)
      db.session.commit()
      flash('Post created!', category='success')
      return redirect(url_for("profile.post", username=user.username, title=title))


  return render_template("create.html", author=current_user)

@profile.route('/<username>/<title>/edit', methods=["GET", "POST"])
@login_required
def edit(username, title):
  user = User.query.filter_by(username=username).first_or_404()
  
  if user != current_user:
    abort(403)

  post = Post.query.filter_by(title=title, author=user).first_or_404()
  
  if request.method == 'POST':
    description = request.form.get('description')
    data = request.form.get('data')

    if not description:
      description = "No description..."

    if len(description) < 4:
      flash('Description must be longer than 3 characters.', category='error')
    elif len(data) < 10:
      flash('Content must be longer than 10 characters.', category='error')
    else:
      post.description = description
      post.content = data
      db.session.commit()
      flash('Post edited!', category='success')
      return redirect(url_for("profile.post", username=user.username, title=title))

  return render_template("edit.html", author=current_user, post=post)

@profile.route('/<username>/<title>/delete', methods=["GET", "POST"])
@login_required
def delete(username, title):
  user = User.query.filter_by(username=username).first_or_404()
  
  if user != current_user:
    abort(403)

  post = Post.query.filter_by(title=title, author=user).first_or_404()
  
  if request.method == 'POST':
    delete = request.form.get('yes')
    if delete is None:
      return redirect(url_for("profile.post", username=user.username, title=post.title))
    
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', category='success')
    return redirect(url_for('profile.prof', username=user.username))

  return render_template("delete.html", author=current_user, post=post)
