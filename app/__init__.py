from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_migrate import Migrate
from flask_moment import Moment
from flask_recaptcha import ReCaptcha
from .config import Config


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
  from .utils import markdown

  app = Flask(__name__)
  app.config.from_object(Config)

  @app.context_processor
  def globals():
    return {
      "markdown": markdown,
      "len": len,
      "str": str,
      "tab": "",
      "app": app
    }

  @app.before_request
  def check_session():
    if request.endpoint == "home.index": return
    if request.endpoint == "static": return

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

  app.register_blueprint(home)
  app.register_blueprint(auth)
  app.register_blueprint(profile)
  app.register_blueprint(post)
  app.register_blueprint(errors)
  
  return app