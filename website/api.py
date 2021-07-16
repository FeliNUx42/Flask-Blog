from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user, logout_user, login_user
from .models import User, Posts
from . import db, valid_username
from markdown import markdown


api = Blueprint('api', __name__)

@api.route("/markdown", methods=["POST"])
def mark():
  if not request.form.get("data"):
    return "<i>empty</i>"
  return markdown(request.form.get("data"), extensions=["extra"])

@api.route("/valid-username", methods=["POST"])
def val_username():
  if not request.form.get("data"):
    return "error"
  return str(valid_username(request.form.get("data"))).lower()
