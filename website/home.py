from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import current_user
from .models import User, Posts
from . import db


home = Blueprint('home', __name__)

@home.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    search = request.form.get('search')
    return 'error: ' + search

  return render_template("home.html", user=current_user)

