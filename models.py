from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from dateutil.relativedelta import relativedelta

db = SQLAlchemy()

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

    def __init__(self, id, company_name, plan_id, paid_thru, is_current, max_users, date=datetime.now()):
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

    def __init__(self, account_id, name, username, password, email, active, activation_link="", password_reset_link="",
    avatar = ""):
        self.account_id = account_id
        self.name = name
        self.username = username
        self.password = password
        self.email = email
        self.active = active
        self.activation_link = activation_link
        self.password_reset_link = password_reset_link
        self.avatar = avatar

class Rating(db.Model):
    __tablename__ = "rating"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    item = db.Column(db.String(50))
    score = db.Column(db.Integer)
    comment = db.Column(db.Text)
    username = db.Column(db.String(35))
    date = db.Column(db.Date)
    hidden = db.Column(db.Integer)
    followup = db.Column(db.Text)
    followup_user = db.Column(db.String(35))
    rater_email = db.Column(db.String(50))
    rater_name = db.Column(db.String(50))
    rater_id = db.Column(db.Integer)

    def __init__(self, account_id, user_id, score, username, rater_email="", rater_name="", rater_id="", comment="",
    hidden=0, date=datetime.now()):
        self.account_id = account_id
        self.user_id = user_id
        self.score = score
        self.username = username
        self.comment = comment
        self.hidden = hidden
        self.date = date
        self.rater_email = rater_email
        self.rater_name = rater_name
        self.rater_id = rater_id

class Team(db.Model):
    __tablename__ = "team"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    team_name = db.Column(db.String(50))
    team_leader_name = db.Column(db.String(35))
    team_leader_id = db.Column(db.Integer)
    avatar = db.Column(db.String(50))

    def __init__(self, account_id, team_name, team_leader_name, team_leader_id, avatar=""):
        self.account_id = account_id
        self.team_name = team_name
        self.team_leader_name = team_leader_name
        self.team_leader_id = team_leader_id
        self.avatar = avatar

class Membership(db.Model):
    __tablename__ = "membership"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)
    is_admin = db.Column(db.Integer)
    permissions = db.Column(db.Integer)

    def __init__(self, account_id, user_id, team_id, is_admin=0, permissions=0):
        self.account_id = account_id
        self.user_id = user_id
        self.team_id = team_id
        self.is_admin = is_admin
        self.permissions = permissions

class Package(db.Model):
    __tablename__ = "package"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    num_users = db.Column(db.Integer)
    monthly_cost = db.Column(db.Float(precision=2))
    annual_cost = db.Column(db.Float(precision=2))
    biennial_cost = db.Column(db.Float(precision=2))
    cost_per_additional_user = db.Column(db.Float(precision=2))

    def __init__(self, name, num_users, monthly_cost, annual_cost, biennial_cost, cost_per_additional_user):
        self.name = name
        self.num_users = num_users
        self.monthly_cost = monthly_cost
        self.annual_cost = annual_cost
        self.biennial_cost = biennial_cost
        self.cost_per_additional_user = cost_per_additional_user

class Rater(db.Model):
    __tablename__ = "rater"

    id = db.Column(db.Integer, primary_key=True)
    user_hash = db.Column(db.String(50))
    reap = db.Column(db.Date)

    def __init__(self, user_hash, reap=datetime.now() + relativedelta(weeks=1)):
        self.user_hash = user_hash
        self.reap = reap

class Token(db.Model):
    __tablename__ = "token"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    expire = db.Column(db.Date)

    def __init__(self, account_id, user_id, token, expire = datetime.now() + relativedelta(weeks=1)):
        self.account_id = account_id
        self.user_id = user_id
        self.token = token
        self.expire = expire

class Billing(db.Model):
    __tablename__ = "billing"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    type = db.Column(db.String(25))
    total = db.Column(db.Integer)
    transaction_id = db.Column(db.String(30))
    date = db.Column(db.DateTime)

    def __init__(self, account_id, type, total, transaction_id, date):
        self.account_id = account_id
        self.type = type
        self.total = total
        self.transaction_id = transaction_id
        self.date = date
