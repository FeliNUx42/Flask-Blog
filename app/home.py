from flask import Blueprint, render_template, request, session, current_app, make_response, url_for
from datetime import datetime, timedelta
from sqlalchemy import or_
from .models import User, Post
from .utils import markdown
from . import csrf


home = Blueprint('home', __name__)

# check __init__.py - line 42
"""
@app.before_request
  def check_session():
    if request.path == "/": return

    if session.get("SEARCH_QUERY"):
      del session["SEARCH_QUERY"]
"""


def get_posts(search, order_by, per_page, pages):
  username = User.query.filter(User.username.ilike(f'%{search}%'))
  user_desc = User.query.filter(User.description.ilike(f'%{search}%'))
  post_title = Post.query.filter(Post.title.ilike(f'%{search}%'))
  post_content = Post.query.filter(or_(Post.description.ilike(f'%{search}%'), Post.content.like(f'%{search}%')))

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
  
  username = username.paginate(pages["username"], per_page, True)
  user_desc = user_desc.paginate(pages["user_desc"], per_page, True)
  post_title = post_title.paginate(pages["post_title"], per_page, True)
  post_content = post_content.paginate(pages["post_content"], per_page, True)

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
  tab = request.args.get("tab", "username")
  order_by = request.args.get("order-by", "latest")
  per_page = request.args.get("per-page", current_app.config['POSTS_PER_PAGE'], type=int)
  default = False

  if search is not None or request.args.get("order-by") or request.args.get("per-page"):
    if session.get("SEARCH_QUERY"):
      session["SEARCH_QUERY"]["pages"][tab] = page
      pages = session["SEARCH_QUERY"]["pages"]
    else:
      pages = {"username": 1, "user_desc":1, "post_title":1, "post_content":1}
    session["SEARCH_QUERY"] = {"search":search, "order_by":order_by, "per_page":per_page, "pages":pages}
  if session.get("SEARCH_QUERY"):
    session["SEARCH_QUERY"]["pages"][tab] = page

    data = get_posts(**session["SEARCH_QUERY"])
  else:
    data = {}
    default = True

  return render_template("main/home.html", **data, default=default, tab=tab)

@home.route("/about")
def about():
  return render_template("main/about.html")

@home.route("/contact")
def contact():
  return render_template("main/contact.html")

@home.route("/markdown", methods=["POST"])
@csrf.exempt
def mark():
  if not request.form.get("data"):
    return "<i>empty</i>"
  return markdown(request.form.get("data"))
  
@home.route("/sitemap")
@home.route("/sitemap.xml")
def sitemap():
  server_name = f"{request.scheme}://{request.host}"

  pages = []

  lastmod = datetime.now() - timedelta(days=10)
  lastmod = lastmod.strftime('%Y-%m-%d')
  for rule in current_app.url_map.iter_rules():
    if 'GET' in rule.methods and len(rule.arguments) == 0 and not rule.endpoint.startswith("auth."):
      pages.append([server_name + rule.rule, lastmod])
  
  users = User.query.all()
  for user in users:
    url = server_name + url_for('profile.prof', username=user.username)
    pages.append([url, lastmod])

  posts = Post.query.all()
  for post in posts:
    url = server_name + url_for('post.pst', username=post.author.username, title=post.title)
    pages.append([url, lastmod])

  sitemap_template = render_template('main/sitemap.xml', pages=pages)
  response = make_response(sitemap_template)
  response.headers['Content-Type'] = 'application/xml'
  return response
