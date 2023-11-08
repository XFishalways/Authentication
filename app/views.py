# -*- coding: utf-8 -*-
# @Author  : XFishalways
# @Time    : 2023/11/6 13:33
# @Function: routes defined
import base64
import os
import logging

import pyotp
import qrcode
from io import BytesIO

# Flask modules
from flask import (
    render_template,
    request,
    url_for,
    redirect,
    send_from_directory,
    flash,
)
from flask_login import login_user, logout_user
from jinja2 import TemplateNotFound

# App modules
from app import app, lm, bc
from app.forms import LoginForm, RegisterForm
from app.models import Users


secret_key = app.config.get("SECRET_KEY")


# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Logout user
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


# Register a new user
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm(request.form)
    msg = None
    success = False
    qr_code = None

    if request.method == "GET":
        return render_template("register.html", form=form, msg=msg, qr_code=qr_code)

    if form.validate_on_submit():
        username = request.form.get("username", "", type=str)
        password = request.form.get("password", "", type=str)
        email = request.form.get("email", "", type=str)

        user = Users.query.filter_by(user=username).first()
        user_by_email = Users.query.filter_by(email=email).first()

        if user or user_by_email:
            msg = "Error: User exists!"
        else:
            pw_hash = bc.generate_password_hash(password)

            totp_secret = pyotp.random_base32()
            user = Users(username, email, pw_hash, totp_secret)
            user.save()

            otp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
                name=username, issuer_name="XFishalways"
            )
            img = qrcode.make(otp_uri)

            buffered = BytesIO()
            img.save(buffered)
            img_bytes = buffered.getvalue()

            img_base64 = base64.b64encode(img_bytes).decode("utf-8")

            msg = "User created successfully. Please save this secret key and scan the QR code with Google Authenticator:"
            success = True
            qr_code = img_base64

    else:
        msg = "Input error"

    return render_template(
        "register.html", form=form, msg=msg, success=success, qr_code=qr_code
    )


# Authenticate user
@app.route("/login", methods=["GET", "POST"])
def login():
    # Declare the login form
    form = LoginForm(request.form)

    msg = None

    if form.validate_on_submit():
        username = request.form.get("username", "", type=str)
        password = request.form.get("password", "", type=str)

        user = Users.query.filter_by(user=username).first()

        if user:
            if bc.check_password_hash(user.password, password):
                totp_code = form.totp_code.data
                totp = pyotp.TOTP(user.totp_secret)
                if totp.verify(totp_code):
                    login_user(user)
                    return redirect(url_for("index"))
                else:
                    msg = "Invalid Google Authenticator code. Please try again."
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown user"

    return render_template("login.html", form=form, msg=msg)


# App main route + generic routing
@app.route("/", defaults={"path": "index"})
@app.route("/<path>")
def index(path):
    try:
        return render_template("index.html")

    except TemplateNotFound:
        return render_template("page-404.html"), 404


# Return sitemap
@app.route("/sitemap.xml")
def sitemap():
    return send_from_directory(os.path.join(app.root_path, "static"), "sitemap.xml")
