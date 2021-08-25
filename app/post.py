from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from .models import User, Post
from . import db, valid_title, confirmed_required


post = Blueprint('post', __name__)


@post.route('/<username>/<title>')
def pst(username, title):
  user = User.query.filter_by(username=username).first_or_404()
  post = Post.query.filter_by(title=title, author=user).first_or_404()

  return render_template("post.html",  author=user, post=post)

@post.route('/<username>/create', methods=["GET", "POST"])
@login_required
@confirmed_required
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
      return redirect(url_for("post.pst", username=user.username, title=title))


  return render_template("create.html", author=current_user)

@post.route('/<username>/<title>/edit', methods=["GET", "POST"])
@login_required
@confirmed_required
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
      return redirect(url_for("post.pst", username=user.username, title=title))

  return render_template("edit.html", author=current_user, post=post)

@post.route('/<username>/<title>/delete', methods=["GET", "POST"])
@login_required
@confirmed_required
def delete(username, title):
  user = User.query.filter_by(username=username).first_or_404()
  
  if user != current_user:
    abort(403)

  post = Post.query.filter_by(title=title, author=user).first_or_404()
  
  if request.method == 'POST':
    delete = request.form.get('yes')
    if delete is None:
      return redirect(url_for("post.pst", username=user.username, title=post.title))
    
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', category='success')
    return redirect(url_for('profile.prof', username=user.username))

  return render_template("delete.html", author=current_user, post=post)
