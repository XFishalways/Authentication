# -*- coding: utf-8 -*-
# @Author  : XFishalways
# @Time    : 2023/11/6 13:03
# @Function: model defined

from app import db
from flask_login import UserMixin


class Users(db.Model, UserMixin):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(500))
    totp_secret = db.Column(db.String(500))
    email_confirmed = db.Column(db.Boolean, default=False)
    email_confirm_token = db.Column(db.String(100), nullable=True)

    def __init__(
        self, user, email, password, totp_secret, email_confirmed, email_confirm_token
    ):
        self.user = user
        self.password = password
        self.email = email
        self.totp_secret = totp_secret
        self.email_confirmed = email_confirmed
        self.email_confirm_token = email_confirm_token

    def __repr__(self):
        return str(self.id) + " - " + str(self.user)

    def save(self):
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self
