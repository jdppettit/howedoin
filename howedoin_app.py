from flask import *
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.mail import *

from credentials import *
from password import *

import stripe
import random
import string
import datetime

from dateutil.relativedelta import relativedelta

app = Flask(__name__)
connectionString = "mysql://%s:%s@%s:3306/%s" % (USERNAME, PASSWORD, HOSTNAME, DATABASE)

app.config['SQLALCHEMY_DATABASE_URI'] = connectionString
db = SQLAlchemy(app)
app.secret_key = SECRET_KEY

app.config.update(
    MAIL_SERVER=EMAIL_SERVER,
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME=EMAIL_USERNAME,
    MAIL_PASSWORD=EMAIL_PASSWORD
)

mail = Mail(app)

# DB MODEL DECS

class Account(db.Model):
    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(25))
    plan_id = db.Column(db.Integer)
    paid_thru = db.Column(db.Date)
    is_current = db.Column(db.Integer)
    stripe_customer = db.Column(db.String(20))
    max_users = db.Column(db.Integer)
    date = db.Column(db.Date)

    def __init__(self, id, company_name, plan_id, paid_thru, is_current, max_users, date=datetime.datetime.now()):
        self.id = id
        self.company_name = company_name
        self.plan_id = plan_id
        self.paid_thru = paid_thru
        self.is_current = is_current
        self.max_users = max_users
        self.date = date

class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    name = db.Column(db.String(35))
    username = db.Column(db.String(35))
    password = db.Column(db.String(50))
    email = db.Column(db.String(40))
    active = db.Column(db.Integer)
    activation_link = db.Column(db.String(10))
    password_reset_link = db.Column(db.String(25))
    avatar = db.Column(db.String(50))

    def __init__(self, id, account_id, name, username, password, email, active, activation_link="", password_reset_link="",
    avatar = ""):
        self.id = id
        self.account_id = account_id
        self.name = name
        self.username = username
        self.password = password
        self.email = email
        self.active = active
        self.activation_link = activation_link
        self.password_reset_link = password_reset_link
        self.avatar = avatar




