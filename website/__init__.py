from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from uuid import uuid4
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

CONFIG = {
  "SECRET_KEY": "chane this",
  "UPLOAD_FOLDER" : "website/static/profile_pictures/"
}

def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = CONFIG["SECRET_KEY"]
  app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
  db.init_app(app)

  app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
  app.config["UPLOAD_FOLDER"] = "website/static/profile_pic"

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

  from .models import User, Posts

  create_database(app)

  login_manager = LoginManager()
  login_manager.login_view = 'auth.login'
  login_manager.init_app(app)

  @login_manager.user_loader
  def load_user(id):
    return User.query.get(int(id))

  return app

def create_database(app):
  if not path.exists('website/' + DB_NAME):
    db.create_all(app=app)
    print('Created database')

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

def valid_username(username):
  from .models import User, Posts
  from main import app

  user = User.query.filter_by(username=username).first()
  pages = list(app.url_map.iter_rules())
  pages = [p.rule[1:] for p in pages if not p.arguments]
  
  if user or username in pages or "/" in username:
    return False
  return True