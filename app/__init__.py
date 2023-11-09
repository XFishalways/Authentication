import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail, Message

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.static_folder = "static"

app.config.from_object("app.config.Config")
ssl_context = app.config.get("SSL_CONTEXT")

oauth = OAuth(app)

db = SQLAlchemy(app)
bc = Bcrypt(app)

lm = LoginManager()
lm.init_app(app)

mail = Mail(app)

sender = app.config.get("MAIL_USERNAME")

from app import views, models
