from sqlalchemy.orm import backref
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class Posts(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  title = db.Column(db.String(128))
  description = db.Column(db.String(10000))
  content = db.Column(db.String(10000))
  created = db.Column(db.DateTime(timezone=True), default=func.now())
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
  password = db.Column(db.String(128))
  posts = db.relationship('Posts', backref="author", lazy=True)

  def __repr__(self):
    return f'User({self.email}, {self.first_name}, {self.last_name})'