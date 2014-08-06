#!/usr/bin/env python2

from __future__ import absolute_import

from flask import *
from flask.ext.login import LoginManager
from flask.ext.mail import *

from credentials import *
from password import *

import stripe
import random
import string

import logging
from logging.handlers import RotatingFileHandler

from ratings import ratings
from login import login
from register import register

from models import db

app = Flask(__name__)

db.init_app(app)

with app.app_context():
    db.create_all()
    db.session.commit()

app.register_blueprint(ratings)
app.register_blueprint(login)
app.register_blueprint(register)

connectionString = "mysql://%s:%s@%s:3306/%s" % (USERNAME, PASSWORD, HOSTNAME, DATABASE)

app.config['SQLALCHEMY_DATABASE_URI'] = connectionString
app.secret_key = SECRET_KEY

app.config.update(
    MAIL_SERVER=EMAIL_SERVER,
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=EMAIL_USERNAME,
    MAIL_PASSWORD=EMAIL_PASSWORD
)

mail = Mail(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/rating')
def rating():
    return render_template("rating.html")

if __name__ == '__main__':
    handler = RotatingFileHandler('howedoin.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', debug=True)
