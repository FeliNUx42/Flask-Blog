from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import current_user
from .models import User, Post
from . import db


home = Blueprint('home', __name__)

@home.route('/')
def index():
  from main import app

  search = request.args.get("search")
  page = request.args.get("page", 1, type=int)
  order_by = request.args.get("order-by", "latest")
  per_page = request.args.get("per-page", app.config['POSTS_PER_PAGE'], type=int)

  if not search:
    if order_by == "latest":
      posts = Post.query.order_by(Post.created.desc())
    elif order_by == "oldest":
      posts = Post.query.order_by(Post.created.asc())
    posts = posts.paginate(page, per_page, True)

  return render_template("home.html", posts=posts)

