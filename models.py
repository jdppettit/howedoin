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
    paid_thru = db.Column(db.DateTime)
    is_current = db.Column(db.Integer)
    stripe_customer = db.Column(db.String(20))
    max_users = db.Column(db.Integer)
    date = db.Column(db.DateTime)
    needs_billing = db.Column(db.Integer)
    total_monthly_bill = db.Column(db.Float)
    subscription_id = db.Column(db.Integer)
    retry_billing = db.Column(db.Integer)
    cancel = db.Column(db.Integer)
    billing_email = db.Column(db.String(50))

    def __init__(self, id, company_name, plan_id, paid_thru, is_current, max_users, subscription_id=0, date=datetime.now(),
    needs_billing=0, total_monthly_bill=0.00, billing_email=""):
        self.id = id
        self.company_name = company_name
        self.plan_id = plan_id
        self.paid_thru = paid_thru
        self.is_current = is_current
        self.max_users = max_users
        self.date = date
        self.needs_billing = needs_billing
        self.total_monthly_bill = total_monthly_bill
        self.subscription_id = subscription_id
        self.billing_email = billing_email

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
    password_reset_expire = db.Column(db.DateTime)
    score = db.Column(db.Integer)

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
        self.score = 0

class Rating(db.Model):
    __tablename__ = "rating"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    item_id = db.Column(db.String(50))
    score = db.Column(db.Integer)
    comment = db.Column(db.Text)
    username = db.Column(db.String(35))
    date = db.Column(db.DateTime)
    hidden = db.Column(db.Integer)
    followup = db.Column(db.Text)
    followup_user = db.Column(db.String(35))
    rater_email = db.Column(db.String(50))
    rater_name = db.Column(db.String(50))
    rater_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)
    duplicate = db.Column(db.Integer)

    def __init__(self, account_id, user_id, team_id, score, username, rater_email="", rater_name="", rater_id="", comment="",
    hidden=0, duplicate=0, item_id=0, date=datetime.now()):
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
        self.team_id = team_id
        self.duplicate = duplicate
        self.item_id = item_id

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
    reap = db.Column(db.DateTime)

    def __init__(self, user_hash, reap=datetime.now() + relativedelta(weeks=1)):
        self.user_hash = user_hash
        self.reap = reap

class Token(db.Model):
    __tablename__ = "token"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    expire = db.Column(db.DateTime)

    def __init__(self, account_id, user_id, token, expire = datetime.now() + relativedelta(weeks=1)):
        self.account_id = account_id
        self.user_id = user_id
        self.token = token
        self.expire = expire

class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    invoice_id = db.Column(db.Integer)
    credit = db.Column(db.Float)
    debit = db.Column(db.Float)
    transaction_id = db.Column(db.String(30))
    date = db.Column(db.DateTime)
    refunded = db.Column(db.Integer)
    refund_id = db.Column(db.String(30))

    def __init__(self, account_id, invoice_id, credit, debit, transaction_id, date):
        self.account_id = account_id
        self.invoice_id = invoice_id
        self.credit = credit
        self.debit = debit
        self.transaction_id = transaction_id
        self.date = date

class Invoice(db.Model):
    __tablename__ = "invoice"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    total = db.Column(db.Float)
    paid = db.Column(db.Integer)
    payment_id = db.Column(db.Integer)
    refunded = db.Column(db.Integer)

    def __init__(self, account_id, total, paid, payment_id=0):
        self.account_id = account_id
        self.total = total
        self.paid = paid
        self.payment_id = payment_id
        self.refunded = 0

class InvoiceItem(db.Model):
    __tablename__ = "invoice_item"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    invoice_id = db.Column(db.Integer)
    credit = db.Column(db.Float)
    debit = db.Column(db.Float)
    item = db.Column(db.String(25))

    def __init__(self, account_id, invoice_id, item, credit=0.00, debit=0.00):
        self.account_id = account_id
        self.invoice_id = invoice_id
        self.item = item
        self.credit = credit
        self.debit = debit

class Subscription(db.Model):
    __tablename__ = "subscription"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    plan = db.Column(db.Integer)
    cost_per_add = db.Column(db.Float)
    extra_users = db.Column(db.Integer)
    start_date = db.Column(db.DateTime)
    paid_thru = db.Column(db.DateTime)
    total_monthly = db.Column(db.Float)
    most_recent = db.Column(db.Integer)
    cancelled = db.Column(db.Integer)
    touch_date = db.Column(db.DateTime)

    def __init__(self, account_id, plan, cost_per_add, extra_users, start_date, paid_thru, total_monthly, most_recent=1):
        self.account_id = account_id
        self.plan = plan
        self.cost_per_add = cost_per_add
        self.extra_users = extra_users
        self.start_date = start_date
        self.paid_thru = paid_thru
        self.total_monthly = total_monthly
        self.most_recent = most_recent

class Permission(db.Model):
    __tablename__ = "permission"

    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    team_id = db.Column(db.Integer)
    permission_type = db.Column(db.Integer)
    permission = db.Column(db.Integer)
    date = db.Column(db.DateTime)

    def __init__(self, account_id, user_id, permission_type, permission, date=datetime.now(), team_id=0):
        self.account_id = account_id
        self.user_id = user_id
        self.permission_type = permission_type
        self.permission = permission
        self.date = date
        self.team_id = team_id

class Administrator(db.Model):
    __tablename__ = "administrator"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25))
    password = db.Column(db.String(50))
    email = db.Column(db.String(50))
    name = db.Column(db.String(50))

    def __init__(self, username, password, email, name):
        self.username = username
        self.password = password
        self.email = email
        self.name = name
