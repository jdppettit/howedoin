
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
from logout import logout
from dashboard import dashboard
from billing import billing
from team import team
from account import account
from user import user
from email_manager import mail
from admin import admin 

from models import db

app = Flask(__name__)

db.init_app(app)

#with app.app_context():
#    db.create_all()
#    db.session.commit()
#    print db.Model.metadata.tables

app.register_blueprint(ratings)
app.register_blueprint(login)
app.register_blueprint(register)
app.register_blueprint(logout)
app.register_blueprint(dashboard)
app.register_blueprint(billing)
app.register_blueprint(team)
app.register_blueprint(account)
app.register_blueprint(user)
app.register_blueprint(admin)

connectionString = "mysql://%s:%s@%s:3306/%s" % (USERNAME, PASSWORD, HOSTNAME, DATABASE)

app.config['SQLALCHEMY_DATABASE_URI'] = connectionString
app.secret_key = SECRET_KEY
app.config['UPLOAD_FOLDER'] = "/srv/howedoin/static/upload/user"

app.config.update(
    MAIL_SERVER=EMAIL_SERVER,
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=EMAIL_USERNAME,
    MAIL_PASSWORD=EMAIL_PASSWORD
)

mail.init_app(app)

with app.app_context():
    db.create_all()
    db.session.commit()


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/rating')
def rating():
    return render_template("rating.html")

@app.route('/email/newuser')
def newuser():
    return render_template("email_create_new_user.html")

@app.route('/test/navbar')
def testnavbar():
    return render_template("navbar_test.html")

if __name__ == '__main__':
    handler = RotatingFileHandler('howedoin.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0', debug=True)
