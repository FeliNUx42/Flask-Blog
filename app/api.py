from flask import Blueprint, request
from . import valid_username, markdown


api = Blueprint('api', __name__)

@api.route("/markdown", methods=["POST"])
def mark():
  if not request.form.get("data"):
    return "<i>empty</i>"
  return markdown(request.form.get("data"))

@api.route("/valid-username", methods=["POST"])
def val_username():
  if not request.form.get("data"):
    return "error"
  return str(valid_username(request.form.get("data"))).lower()
