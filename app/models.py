from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import backref
from . import db
from flask_login import UserMixin
from datetime import datetime


class Post(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(128))
  description = db.Column(db.String(10000))
  content = db.Column(db.String(10000))
  created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def __repr__(self):
    return f'Post({self.title}, {self.description}, {self.content})'


class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  email = db.Column(db.String(128), unique=True)
  username = db.Column(db.String(128), unique=True)
  first_name = db.Column(db.String(128))
  last_name = db.Column(db.String(128))
  description = db.Column(db.String(1000), default="No description...")
  profile_pic = db.Column(db.String(128), default="default.png")
  password_hash = db.Column(db.String(128))
  posts = db.relationship('Post', backref="author", lazy=True)

  @property
  def password(self):
    raise AttributeError("password is not a readable attribute")

  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)
  
  def verify_password(self, password):
    return check_password_hash(self.password_hash, password)

  def __repr__(self):
    return f'User({self.id}, {self.username}, {self.email})'