import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from authlib.integrations.flask_client import OAuth

# Grabs the folder where the script runs.
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

# Setup databaselm.init_app(app)
# @app.before_first_request
# def initialize_database():
#     db.create_all()

from app import views, models
