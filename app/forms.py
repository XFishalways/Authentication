# -*- coding: utf-8 -*-
# @Author  : XFishalways
# @Time    : 2023/11/6 14:23
# @Function: form edit

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import Email, DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    totp_code = StringField("Google Authenticator Code", validators=[DataRequired()])
    submit = SubmitField("Login")


class RegisterForm(FlaskForm):
    name = StringField("Name")
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])


class ForgotForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Confirm")


class ResetForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    passwordConfirm = PasswordField("PasswordConfirm", validators=[DataRequired()])
    submit = SubmitField("Confirm")
