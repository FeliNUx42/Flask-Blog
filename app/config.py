import os

class Config:
  DEBUG = True
  SECRET_KEY = os.environ.get("SECRET_KEY", "922c979c6f04da99b5ad58642f5e2ec1")
  PROFILE_PICTURE_FOLDER = "static/profile_pictures/"
  MAX_CONTENT_LENGTH = 16 * 1024 * 1024
  POSTS_PER_PAGE = 10
  SERVER_NAME = os.environ.get("SERVER_NAME", "127.0.0.1:5000")

  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')\
    .replace('postgres://', 'postgresql://') or 'sqlite:///database.db'

  SQLALCHEMY_TRACK_MODIFICATIONS = False

  MAIL_SERVER = "smtp.googlemail.com"
  MAIL_PORT = 587
  MAIL_USE_TLS = True
  MAIL_USERNAME = os.environ.get("MAIL_USER")
  MAIL_PASSWORD = os.environ.get("MAIL_PASS")

  RECAPTCHA_SITE_KEY = os.environ.get("RECAPTCHA_SITE_KEY")
  RECAPTCHA_SECRET_KEY = os.environ.get("RECAPTCHA_SECRET_KEY")

