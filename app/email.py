from flask import current_app
from flask_mail import Message
from . import mail


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