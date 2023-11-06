import os
import sys

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)


# prefix = "mysql://username:password@server/db"
# app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'database.db')
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#
# db.init_app(app)


@app.route('/', methods=("GET", "POST"))
def hello():
    return redirect(url_for('login_get'))


@app.route('/login', methods=["GET"])
def login_get():
    return render_template("login.html")


@app.route('/login', methods=["POST"])
def login_post():
    username = request.form.get("username")
    password = request.form.get("password")

    # TODO

    return "success"


@app.route('/register', methods=['GET'])
def register_get():
    return render_template("register.html")


if __name__ == "__main__":
    try:
        app.run(debug=True)
    except Exception as e:
        print(str(e))
