from flask import Blueprint, render_template, request, session, current_app
from sqlalchemy import or_
from .models import User, Post


home = Blueprint('home', __name__)

# check __init__.py - line 42
"""
@app.before_request
  def check_session():
    if request.path == "/": return

    if session.get("SEARCH_QUERY"):
      del session["SEARCH_QUERY"]
"""


def get_posts(search, order_by, per_page, page=1):
  username = User.query.filter(User.username.like(f'%{search}%'))
  user_desc = User.query.filter(User.description.like(f'%{search}%'))
  post_title = Post.query.filter(Post.title.like(f'%{search}%'))
  post_content = Post.query.filter(or_(Post.description.like(f'%{search}%'), Post.content.like(f'%{search}%')))

  if order_by == "latest":
    username = username.order_by(User.created.desc())
    user_desc = user_desc.order_by(User.created.desc())
    post_title = post_title.order_by(Post.created.desc())
    post_content = post_content.order_by(Post.created.desc())
  elif order_by == "oldest":
    username = username.order_by(User.created.asc())
    user_desc = user_desc.order_by(User.created.asc())
    post_title = post_title.order_by(Post.created.asc())
    post_content = post_content.order_by(Post.created.asc())
  
  username = username.paginate(page, per_page, True)
  user_desc = user_desc.paginate(page, per_page, True)
  post_title = post_title.paginate(page, per_page, True)
  post_content = post_content.paginate(page, per_page, True)

  return {
    "username": username,
    "user_description": user_desc,
    "post_title": post_title,
    "post_content": post_content,
    "search": search
  }

@home.route('/')
def index():
  search = request.args.get("search")
  page = request.args.get("page", 1, type=int)
  order_by = request.args.get("order-by", "latest")
  per_page = request.args.get("per-page", current_app.config['POSTS_PER_PAGE'], type=int)
  default = False

  if search or order_by or per_page or page:
    session["SEARCH_QUERY"] = {"search":search, "order_by":order_by, "per_page":per_page, "page":page}
  if session.get("SEARCH_QUERY"):
    data = get_posts(**session["SEARCH_QUERY"])
  else:
    default = True

  print(default, session.get("SEARCH_QUERY"))
  return render_template("home.html", **data, default=default)

