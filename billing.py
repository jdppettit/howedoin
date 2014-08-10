from flask import *
from models import db, Account, Billing
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

def checkExistingBilling(id):
    check = Billing.query.filter_by(transaction_id=id).first()
    if check:
        return True
    else:
        return False

@billing.route('/billing/checkout', methods=['POST'])
@billing.route('/checkout', methods=['POST'])
def checkout():
    if request.method == "POST":
        if request.form['plan'] and request.form['cost'] and request.form['account_id'] and request.form['stripeToken']:
            token = request.form['stripeToken']
            plan = ""

            if request.form['plan'] == "1":
                plan = "business"
            elif request.form['plan'] == "2":
                plan = "enterprise"

            customer = stripe.Customer.create(
                card=token,
                plan=plan,
                email=session['email'],
                metadata={'account_id' : request.form['account_id']}
            )

            account = Account.query.filter_by(id=request.form['account_id']).first()
            account.stripe_customer = customer['id']
            db.session.commit()

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
        if session['account_id']:
            # this needs to pass the subscription ID back
            you = Account.query.filter_by(id=session['account_id']).first()
            customer = stripe.Customer.retrieve(you.stripe_customer)
        else:
            return render_template("login.html", error="You must be logged in to do this.")
        return render_template("billing_canceled.html")

@billing.route('/billing/edit', methods=['POST','GET'])
def editBilling():
    if request.method == "GET":
        return render_template("billing_edit.html")
    elif request.method == "POST":
        print "does the thing"

@billing.route('/billing/hooks', methods=['POST'])
def hooks():
    req = request.get_json()
    
    reqType = req['type']
    customerID = req['data']['object']['customer']
    transaction_id = req['id']
    transaction_date = datetime.now()
    customerObj = Account.query.filter_by(stripe_customer=customerID).first()
    
    resp = make_response()

    if reqType == "customer.created":
        reply = checkExistingBilling(transaction_id)
        if reply:
            # done
            resp.status_code=200
            return resp
        else:
            newBilling = Billing(customerObj.id, "customer_created", 0, transaction_id, transaction_date)

            db.session.add(newBilling)
            db.session.commit()
    
            resp.status_code=200
            return resp
    elif reqType == "customer.subscription.created":
        reply = checkExistingBilling(transaction_id)
        if reply:
            # done
            resp.status_code=200
            return resp
        else:
            newBilling = Billing(customerObj.id, "customer_sub_created", 0, transaction_id, transaction_date)
    
            db.session.add(newBilling)
            db.session.commit()

            resp.status_code=200
            return resp
    elif reqType == "invoice.created":
        reply = checkExistingBilling(transaction_id)
        if reply:
            # done
            resp.status_code=200
            return resp
        else:
            amount = req['data']['object']['total']
            amount = amount / 100
            newBilling = Billing(customerObj.id, "invoice_created", amount, transaction_id, transaction_date)

            db.session.add(newBilling)
            db.session.commit()

            resp.status_code=200
            return resp
    elif reqType == "charge.succeeded":
        reply = checkExistingBilling(transaction_id)
        if reply:
            # done
            resp.status_code=200
            return resp
        else:
            amount = req['data']['object']['amount']
            amount = amount / 100
            newBilling = Billing(customerObj.id, "charge_succeeded", amount, transaction_id, transaction_date)

            db.session.add(newBilling)
            db.session.commit()

            resp.status_code=200
            return resp
    elif reqType == "invoice.payment_succeeded":
        reply = checkExistingBilling(transaction_id)
        if reply:
            # done
            resp.status_code=200
            return resp
        else:
            amount = req['data']['object']['total']
            amount = amount / 100
            newBilling = Billing(customerObj.id, "payment_succeeded", amount, transaction_id, transaction_date)
    
            db.session.add(newBilling)
            db.session.commit()

            resp.status_code=200
            return resp
    else:
        response.status_code=402
        return response

