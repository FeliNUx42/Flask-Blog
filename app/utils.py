from flask import current_app, flash, redirect, url_for
from flask_login import current_user
from functools import wraps
from os import path
from uuid import uuid4
from PIL import Image
import requests


def valid_type(filename):
  extensions = (".png", ".jpg", ".jpeg")
  for ext in extensions:
    if filename.endswith(ext):
      return True
  return False

def valid_username(username, id=0):
  from .models import User

  user = User.query.filter_by(username=username).first()
  pages = list(current_app.url_map.iter_rules())
  _pages = [p.rule.split("/")[-1] for p in pages if not p.arguments]
  
  if user and user.id != id:
    return False

  if username in _pages or "/" in username:
    return False

  return True

def valid_title(title, id=0):
  from .models import Post

  post = Post.query.filter_by(title=title).first()
  pages = list(current_app.url_map.iter_rules())
  _pages = ["/"+p.rule.split("/")[-1] for p in pages if p.arguments == {'username'} and p.endpoint != 'profile.prof']
  pages_ = ["/"+p.rule.split("/")[-1]  for p in pages if p.arguments == {"username", "title"} and p.endpoint != 'post.pst']
  
  if post and post.id != id:
    return False

  if title in _pages:
    return False
  
  for node in pages_:
    if node in title:
      return False

  return True

def save_file(form_pic):
  hex = uuid4().hex
  _, ext = path.splitext(form_pic.filename)
  picture_fn = hex + ext
  picture_path = path.join(current_app.root_path, current_app.config["PROFILE_PICTURE_FOLDER"], picture_fn)

  output_size = (200, 200)
  i = Image.open(form_pic)
  i.thumbnail(output_size)
  i.save(picture_path)

  return picture_fn

def confirmed_required(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not current_user.confirmed:
            flash('Please confirm your account!', 'error')
            return redirect(url_for('auth.unconfirmed'))
        return func(*args, **kwargs)

    return decorated_function

def markdown(text):
  return requests.post("https://api.github.com/markdown", json={"text":text}).text