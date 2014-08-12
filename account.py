from flask import *
from models import db, Subscription, Invoice, InvoiceItem, Account, Payment, User
from functions import *

account = Blueprint('account', __name__, template_folder="templates")

def getTotal(account_id):
    invoices = Invoice.query.filter_by(account_id=account_id).all()
    payments = Payment.query.filter_by(account_id=account_id).all()
    invoiceTotal = 0.00
    paymentTotal = 0.00
    for invoice in invoices:
        invoiceTotal += invoice.total
    for payment in payments:
        paymentTotal += payment.debit
        paymentTotal -= payment.credit
    account_balance = invoiceTotal - paymentTotal
    return account_balance

def getCurrentUsers(account_id):
    users = User.query.filter_by(account_id=account_id).all()
    length = len(users)
    return length

def getPaidThru(account_id):
    subscription = Subscription.query.filter_by(account_id=account_id).first()
    return subscription.paid_thru

def getMaxUsers(account_id):
    account = Account.query.filter_by(id=account_id).first()
    return account.max_users

def getMonthlyCost(account_id):
    subscription = Subscription.query.filter_by(account_id=account_id).first()
    return subscription.total_monthly

def getPlan(account_id):
    account = Account.query.filter_by(id=account_id).first()
    return account.plan_id

def getPlanName(plan):
    if plan == 0:
        return "Free"
    elif plan == 1:
        return "Business"
    elif plan == 2:
        return "Enterprise"

def getInvoices(account_id):
    invoices = Invoice.query.filter_by(account_id=account_id).all()
    return invoices

@account.route('/dashboard/account/billing')
def accountBilling():
    resp = checkLogin()
    if resp:
        account_id = session['account_id']
        plan_id = getPlan(account_id)
        plan_name = getPlanName(plan_id)
        currentUsers = getCurrentUsers(account_id)
        maxUsers = getMaxUsers(account_id)
        invoices = getInvoices(account_id)
        monthly_cost = getMonthlyCost(account_id)
        paid_thru = getPaidThru(account_id)
        account_balance = getTotal(session['account_id'])
        return render_template("dashboard_account_billing.html", account_balance=account_balance, plan=plan_name,
        current_users=currentUsers, max_users=maxUsers, invoices=invoices, monthly_cost=monthly_cost,
        paid_thru=paid_thru)
    else:
        return notLoggedIn()
