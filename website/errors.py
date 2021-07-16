from flask import Blueprint, render_template
from flask_login import current_user

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(403)
def error_403(error):
  title = "You don't have permission to do that (403)"
  message = "Please check your account and try again"
  return render_template("error.html", user=current_user, title=title, message=message)

@errors.app_errorhandler(404)
def error_404(error):
  title = "Oops. Page Not Found (404)"
  message = "That page does not exist. Please try a different location"
  return render_template("error.html", user=current_user, title=title, message=message)

@errors.app_errorhandler(500)
def error_500(error):
  title = "Something went wrong (500)"
  message = "We're experiencing some trouble on our end. Please try again in the near future"
  return render_template("error.html", user=current_user, title=title, message=message)
