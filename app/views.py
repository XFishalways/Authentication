# -*- coding: utf-8 -*-
# @Author  : XFishalways
# @Time    : 2023/11/6 13:33
# @Function: routes defined
import base64
import os
import logging
import urllib

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

from itsdangerous import URLSafeTimedSerializer
from flask_login import login_user, logout_user, current_user, LoginManager
from flask_mail import Mail, Message
from itsdangerous import Serializer
from jinja2 import TemplateNotFound
from itsdangerous import SignatureExpired, BadSignature
from werkzeug.security import generate_password_hash

from app import app, lm, bc, mail, db, sender
from app.forms import LoginForm, RegisterForm, ForgotForm, ResetForm
from app.models import Users


secret_key = app.config.get("SECRET_KEY")


# provide login manager with load_user callback
@lm.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# logout user
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


# send email
def send_confirmation_email(user):
    s = Serializer(secret_key)
    token = s.dumps({"user_id": user.id})

    confirm_url = url_for("confirm_email", token=token, _external=True)

    subject = "Confirm Your Email"
    body = f"Thank you for registering. Please confirm your email by clicking on the link: {confirm_url}"

    message = Message(subject, sender=sender, recipients=[user.email], body=body)
    mail.send(message)


# register a new user
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
            user = Users(
                username, email, pw_hash, totp_secret, False, email_confirm_token=""
            )
            user.save()

            db.session.add(user)
            db.session.commit()

            send_confirmation_email(user)

            otp_uri = pyotp.totp.TOTP(totp_secret).provisioning_uri(
                name=username, issuer_name="XFishalways"
            )
            img = qrcode.make(otp_uri)

            buffered = BytesIO()
            img.save(buffered)
            img_bytes = buffered.getvalue()

            img_base64 = base64.b64encode(img_bytes).decode("utf-8")

            msg = (
                "User created successfully. "
                "Please check your email for confirmation and scan the QR code with Google Authenticator."
                "You need BOTH to login."
            )
            success = True
            qr_code = img_base64

    else:
        msg = "Input error"

    return render_template(
        "register.html", form=form, msg=msg, success=success, qr_code=qr_code
    )


# token confirmed
def confirm_email_token(token):
    s = Serializer(secret_key)
    try:
        data = s.loads(token)
        return data["user_id"]
    except SignatureExpired:
        return None
    except BadSignature:
        return None


# confirm email
@app.route("/confirm_email/<token>")
def confirm_email(token):
    user_id = confirm_email_token(token)

    if user_id is not None:
        user = Users.query.get(user_id)

        if user:
            user.email_confirmed = True
            db.session.commit()
            flash("Email confirmed successfully!", "success")
        else:
            flash("Invalid user!", "error")
    else:
        flash("Invalid confirmation link or link has expired", "error")

    return redirect(url_for("login"))


# authenticate user
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
                if user.email_confirmed:
                    if totp.verify(totp_code):
                        login_user(user)
                        return redirect(url_for("index"))
                    else:
                        msg = "Invalid Google Authenticator code. Please try again."
                else:
                    msg = "Email account unconfirmed. Please go click the confirm link in the email we just sent to you."
            else:
                msg = "Wrong password. Please try again."
        else:
            msg = "Unknown user"

    return render_template("login.html", form=form, msg=msg)


# retrieve password
@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    if current_user.is_authenticated:
        return redirect("/")

    form = ForgotForm(request.form)
    msg = None

    if request.method == "POST":
        email = request.form["email"]
        user = Users.query.filter_by(email=email).first()
        if user:
            serializer = Serializer(secret_key=secret_key)
            token = serializer.dumps(user.email, salt="reset-password")
            reset_link = (
                request.url_root + "reset_password/" + urllib.parse.quote(token)
            )
            message = Message(
                "Reset Your Password",
                sender=sender,
                recipients=[user.email],
            )
            message.body = f"Click the link to reset your password: {reset_link}"
            mail.send(message)
            msg = "An email has been sent with instructions to reset your password."
        else:
            msg = "Email address not found."
    return render_template("forgot_password.html", form=form, msg=msg)


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect("/")

    form = ResetForm(request.form)
    msg = None
    success = False

    try:
        serializer = Serializer(secret_key=secret_key)
        email = serializer.loads(token, salt="reset-password", max_age=3600)
    except:
        msg = "The reset password link is invalid or has expired."
        return redirect("/forgot")

    if request.method == "POST":
        password = request.form["password"]
        passwordConfirm = request.form["passwordConfirm"]
        if password != passwordConfirm:
            msg = "Please enter same password twice."
        else:
            user = Users.query.filter_by(email=email).first()
            user.password = bc.generate_password_hash(password)
            db.session.commit()
            msg = "Your password has been reset successfully."
            success = True

    return render_template(
        "reset_password.html", form=form, msg=msg, success=success, token=token
    )


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
