from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import backref
from . import db
from flask_login import UserMixin
from flask import current_app
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

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
  public_email = db.Column(db.Boolean, default=True)
  username = db.Column(db.String(128), unique=True)
  first_name = db.Column(db.String(128))
  last_name = db.Column(db.String(128))
  description = db.Column(db.String(1000), default="No description...")
  created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
  confirmed = db.Column(db.Boolean, default=False)
  profile_pic = db.Column(db.String(128), default="default.png")
  password_hash = db.Column(db.String(128))
  posts = db.relationship('Post', backref="author", lazy=True)

  followed = db.relationship(
    'User', secondary=followers,
    primaryjoin=(followers.c.follower_id == id),
    secondaryjoin=(followers.c.followed_id == id),
    backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')
  
  def follow(self, user):
    if not self.is_following(user) and self != user:
      self.followed.append(user)

  def unfollow(self, user):
    if self.is_following(user):
      self.followed.remove(user)

  def is_following(self, user):
    return self.followed.filter(
      followers.c.followed_id == user.id).count() > 0

  @property
  def password(self):
    raise AttributeError("password is not a readable attribute")

  @password.setter
  def password(self, password):
    self.password_hash = generate_password_hash(password)
  
  def verify_password(self, password):
    return check_password_hash(self.password_hash, password)
  
  def get_token(self, command, expire_sec=1800):
    s = Serializer(current_app.config['SECRET_KEY'], expire_sec)
    return s.dumps({'user_id': self.id, 'command': command}).decode('utf-8')
  
  @staticmethod
  def verify_token(token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
      data = s.loads(token)
    except:
      return None, None
    return User.query.get(data['user_id']), data['command']


  def __repr__(self):
    return f'User({self.id}, {self.username}, {self.email})'