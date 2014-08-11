from flask import *
from models import db, Account, Invoice, InvoiceItem, Payment, Subscription
from dateutil.relativedelta import relativedelta
from datetime import datetime

import stripe
import pprint

stripe.api_key = "sk_test_XyBItKO0iLZssC4uqGCLOOWd"

billing = Blueprint('billing', __name__, template_folder='templates')

def updatePaidThru(account):
    newExpiry = datetime.now() + relativedelta(months=1)
    account.paid_thru = newExpiry
    db.session.commit()

def updateSubscriptionID(account_id, subscription_id):
    account = Account.query.filter_by(id=account_id).first()
    account.subscription_id = subscription_id
    db.session.commit()
    return 1

def updateIsCurrent(account_id):
    account = Account.query.filter_by(id=account_id).first()
    account.is_current = 1
    db.session.commit()
    return 1

def makeInvoice(account_id, cost, is_paid, payment_id=0):
    newInvoice = Invoice(account_id, cost, is_paid, payment_id)
    db.session.add(newInvoice)
    db.session.commit()
    db.session.refresh(newInvoice)
    return newInvoice.id

def makeInvoiceLineItem(account_id, invoice_id, item, credit=0.00, debit=0.00):
    newLineItem = InvoiceItem(account_id, invoice_id, item, credit, debit)
    db.session.add(newLineItem)
    db.session.commit()
    return 1

def makePayment(account_id, invoice_id, credit, debit, transaction_id, date=datetime.now()):
    newPayment = Payment(account_id, invoice_id, credit, debit, transaction_id, date)
    invoice = Invoice.query.filter_by(id=invoice_id).first()
    invoice.paid = 1
    db.session.add(newPayment)
    db.session.commit()
    return 1

def getTotal(plan_id, extra_users):
    plan_id = int(plan_id)
    extra_users = int(extra_users)

    if plan_id == 1:
        total = 0.00
        total = total + 10.00
        userCost = 0.00
        userCost = 3.00 * extra_users
        total = total + userCost
        return total
    elif plan_id == 2:
        total = 0.00
        total = total + 10.00
        userCost = 0.00
        userCost = 2.50 * extra_users
        total = total + userCost
        return total
 
def makeSubscription(account_id, plan, extra_users):
    plan = int(plan)
    cost_per_add = 0.00
    if plan == 1:
        cost_per_add = 3.00
    elif plan == 2:
        cost_per_add = 2.50
    newSubscription = Subscription(account_id, plan, cost_per_add, extra_users, datetime.now(), datetime.now() +
    relativedelta(months=1), getTotal(plan, extra_users))
    db.session.add(newSubscription)
    db.session.commit()
    db.session.refresh(newSubscription)
    return newSubscription.id

def getCost(plan_id):
    plan_id = int(plan_id)
    if plan_id == 1:
        return 10.00
    elif plan_id == 2:
        return 25.00

def cancelSubscription(account_id):
    subscription = Subscription.query.filter_by(account_id=account_id).first()
    subscription.cancelled = 1
    db.session.commit()

@billing.route('/billing/checkout', methods=['POST'])
@billing.route('/checkout', methods=['POST'])
def checkout():
    if request.method == "POST":
        if request.form['plan'] and request.form['cost'] and request.form['account_id'] and request.form['stripeToken']:
            token = request.form['stripeToken']
            
            customer = stripe.Customer.create(
                card=token,
                email=session['email'],
                metadata={'account_id' : request.form['account_id']}
            )
            account = Account.query.filter_by(id=request.form['account_id']).first()
            account_id = account.id
            customer_id = customer['id']
            account.stripe_customer = customer['id']
            db.session.commit()

            invoice_id = makeInvoice(account_id, getCost(request.form['plan']), 0)
            
            if request.form['plan'] == "1":
                makeInvoiceLineItem(account_id, invoice_id, "Howedoin Business Plan",
                debit=getCost(request.form['plan']))
            elif request.form['plan'] == "2":
                makeInvoiceLineItem(account_id, invoice_id, "Howedoin Enterprise Plan",
                debit=getCost(request.form['plan']))

            try:
                cost = getCost(request.form['plan'])
                cost = cost * 100
                cost = int(cost)
                charge = stripe.Charge.create(
                    amount=cost,
                    currency="usd",
                    customer=customer_id,
                    description="Howedoin")
            except stripe.CardError, e:
                # card declined
                return render_template("failed.html")
            
            updatePaidThru(account)
            subscription_id = makeSubscription(account_id, request.form['plan'], 0)
            updateSubscriptionID(account_id, subscription_id)
            updateIsCurrent(account_id)
            makePayment(account_id, invoice_id, cost, 0.00, charge['id'])
            return render_template("done.html")
        else:
            return render_template("billing.html", error="Something went wrong, your card has not been billed. Please try again.") # need to add in the variables again
    else:
        abort(404)

@billing.route('/billing/cancel', methods=['POST','GET'])
def cancelBilling():
    if request.method == "GET":
        return render_template("billing_cancel.html")
    elif request.method == "POST":
        if session['account_id'] and request.form['confirm']:
            # this needs to pass the subscription ID back
            you = Account.query.filter_by(id=session['account_id']).first()
            cancelSubscription(you.id)
            return render_template("billing_cancelled.html")
        else:
            return render_template("login.html", error="You must be logged in to do this.")

@billing.route('/billing/edit', methods=['POST','GET'])
def editBilling():
    if request.method == "GET":
        return render_template("billing_edit.html")
    elif request.method == "POST":
        print "does the thing"
