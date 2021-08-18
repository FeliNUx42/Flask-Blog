from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from uuid import uuid4
from flask_login import LoginManager
from .config import Config
import requests

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = "error"
@login_manager.user_loader
def load_user(id):
  from .models import User
  return User.query.get(int(id))


def create_app():
  from .models import User, Post

  app = Flask(__name__)
  app.config.from_object(Config)

  db.init_app(app)
  db.create_all(app=app)

  login_manager.init_app(app)

  from .home import home
  from .auth import auth
  from .profile import profile
  from .errors import errors
  from .api import api

  app.register_blueprint(home)
  app.register_blueprint(auth)
  app.register_blueprint(profile)
  app.register_blueprint(errors)
  app.register_blueprint(api)

  return app


def valid_type(filename):
  print(filename)
  extensions = (".png", ".jpg", ".jpeg")
  for ext in extensions:
    print(ext)
    if filename.endswith(ext):
      return True
  return False

def custom_filename(filename):
  _, ext = path.splitext(filename)
  return str(uuid4()) + ext

def valid_username(username, id=0):
  from .models import User
  from main import app

  user = User.query.filter_by(username=username).first()
  pages = list(app.url_map.iter_rules())
  pages = [p.rule[1:] for p in pages if not p.arguments]
  
  if user and user.id != id:
    return False

  if username in pages or "/" in username:
    return False

  return True

def markdown(text):
  return requests.post("https://api.github.com/markdown", json={"text":text}).text