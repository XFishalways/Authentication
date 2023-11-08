# -*- coding: utf-8 -*-
# @Author  : XFishalways
# @Time    : 2023/11/6 13:33
# @Function: config

import os
from decouple import config


class Config:
    CSRF_ENABLED = True

    # Set up the App SECRET_KEY
    SECRET_KEY = config("SECRET_KEY", default="XFIsha1wAys")

    HOSTNAME = "127.0.0.1"
    PORT = "3306"
    DATABASE = "auth"
    USERNAME = "root"
    PASSWORD = "XFish_-141336"
    DB_URI = "mysql+pymysql://{}:{}@{}:{}/{}".format(
        USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE
    )
    SQLALCHEMY_DATABASE_URI = DB_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True

    SSL_CERT = "ssl.crt"
    SSL_KEY = "ssl.key"
    SSL_CONTEXT = (SSL_CERT, SSL_KEY)
