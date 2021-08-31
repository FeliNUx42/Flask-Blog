from flask import Flask, session, request, current_app, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from os import path
from PIL import Image
from uuid import uuid4
from functools import wraps
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_moment import Moment
from flask_recaptcha import ReCaptcha
from .config import Config
import requests

db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
moment = Moment()
csrf = CSRFProtect()
recaptcha = ReCaptcha()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = "error"
login_manager.refresh_view = "/login?reauth=1"
login_manager.needs_refresh_message_category = "error"

@login_manager.user_loader
def load_user(id):
  from .models import User
  return User.query.get(int(id))


def create_app():
  from .models import User, Post

  app = Flask(__name__)
  app.config.from_object(Config)

  @app.context_processor
  def globals():
    return {
      "markdown": markdown,
      "len": len,
      "str": str,
      "app": app
    }

  @app.before_request
  def check_session():
    if request.path == "/": return

    if session.get("SEARCH_QUERY"):
      del session["SEARCH_QUERY"]

  db.init_app(app)
  db.create_all(app=app)
  mail.init_app(app)
  migrate.init_app(app, db)
  moment.init_app(app)
  login_manager.init_app(app)
  csrf.init_app(app)
  recaptcha.init_app(app)

  from .home import home
  from .auth import auth
  from .profile import profile
  from .post import post
  from .errors import errors
  from .api import api

  app.register_blueprint(home)
  app.register_blueprint(auth)
  app.register_blueprint(profile)
  app.register_blueprint(post)
  app.register_blueprint(errors)
  app.register_blueprint(api)

  return app


def valid_type(filename):
  extensions = (".png", ".jpg", ".jpeg")
  for ext in extensions:
    if filename.endswith(ext):
      return True
  return False

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

def get_link(route, token):
  if current_app.config["SERVER_NAME"] == "127.0.0.1:5000":
    return f"http://{current_app.config['SERVER_NAME']}/{route}/{token}"
  else:
      return f"https://{current_app.config['SERVER_NAME']}/{route}/{token}"

def send_reset_email(user):
  if not user:
    return
  
  token = user.get_token(command="reset-password")
  
  msg = Message("Password Reset Request", sender="noreply@blogopedia.com", recipients=[user.email])
  with current_app.app_context(), current_app.test_request_context():
    msg.body = f"""To reset your password, please visit the following link:
{ get_link("reset-password", token) }

If you did not make this request then simply ignore this email and no changes will be made."""

  mail.send(msg)

def send_confirm_email(user):
  token = user.get_token(command="confirm-account")
  
  msg = Message("Welcome to Blogopedia", sender="noreply@blogopedia.com", recipients=[user.email])
  with current_app.app_context(), current_app.test_request_context():
    msg.body = f"""To confirm your email for the account, please visit the following link:
{ get_link("confirm", token) }

If you did not create an account then simply ignore this email and no changes will be made."""

  mail.send(msg)

def send_delete_email(user):
  token = user.get_token(command="delete-account")
  
  msg = Message("Leave Blogopedia", sender="noreply@blogopedia.com", recipients=[user.email])
  with current_app.app_context(), current_app.test_request_context():
    msg.body = f"""To delete your account for the account, please visit the following link:
{ get_link(user.username+"/delete-account", token) }

If you don't want to delete your account then simply ignore this email and no changes will be made."""

  mail.send(msg)