import os
from decouple import config

import app


class Config:
    CSRF_ENABLED = True

    # Set up the App SECRET_KEY
    SECRET_KEY = config("SECRET_KEY", default="S#perS3crEt_007")

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
