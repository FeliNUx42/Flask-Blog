import os

class Config:
  DEBUG = True
  SECRET_KEY = os.environ.get("SECRET_KEY", "922c979c6f04da99b5ad58642f5e2ec1")
  UPLOAD_FOLDER = "app/static/profile_pictures/"
  SQLALCHEMY_DATABASE_URI = f'sqlite:///database.db'
  MAX_CONTENT_LENGTH = 16 * 1024 * 1024
