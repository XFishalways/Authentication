# -*- coding: utf-8 -*-
# @Author  : XFishalways
# @Time    : 2023/11/6 13:03
# @Function: model defined

from app import db
from flask_login import UserMixin


class Users(db.Model, UserMixin):
    __tablename__ = "Users"

    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(500))
    totp_secret = db.Column(db.String(500))

    def __init__(self, user, email, password, totp_secret):
        self.user = user
        self.password = password
        self.email = email
        self.totp_secret = totp_secret

    def __repr__(self):
        return str(self.id) + " - " + str(self.user)

    def save(self):
        # inject self into db session
        db.session.add(self)

        # commit change and save the object
        db.session.commit()

        return self
