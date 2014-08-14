from flask import *
from functions import *
from models import *
from billing import *
from dateutil.relativedelta import relativedelta

import stripe
import datetime

def getAllSubscriptions():
    subscriptions = Subscription.query.filter_by(id>0).all()
    return subscriptions

def getBillableSubscriptions():
    now = datetime.datetime.now()
    subscriptions = Subscription.query.filter_by(Subscription.paid_thru<=now).all()

def getBillableAccounts(subscriptions):
    now = datetime.datetime.now()
    needsBilling = []
    for subscription in subscriptions:
        if subscription.paid_thru < now:
            needsBilling.append(subscription.account_id)
    return needsBilling
            
def updateSubscriptionPaidThru(subscription):
    subscription.paid_thru = datetime.datetime.now() + relativedelta(months=1)
    db.session.commit(subscription)

def doBilling():
    billableSubs = getBillableSubscriptions()

    for sub in billableSubs:
        plan_name = ""
        per_user = 0.00

        if sub.plan == 1:
            plan_name = "Howedoin Business"
            per_user = 3.00
        elif sub.plan == 2:
            plan_name = "Howedoin Enterprise"
            per_user = 2.50

        account = Account.query.filter_by(id=sub.account_id).first()
        stripe_customer = account.stripe_customer
        # make invoice
        invoice_id = makeInvoice(account.id, sub.total_monthly, 0)
        # add line items
        makeInvoiceLineItem(account.id, invoice_id, plan_name, debit=sub.total_monthly)
        extra_user_cost = sub.extra_users * per_user
        if sub.extra_users > 0:
            makeInvoiceLineItem(account.id, invoice_id, "Extra Users", debit=extra_user_cost)
        
        invoice_total = sub.total_monthly + extra_user_cost

        res, charge = makeCharge(stripe_customer, invoice_total, "Howedoin - Monthly Recurring")

        if res:
            makePayment(account.id, invoice_id, invoice_total, 0, charge['id'])
            updateSubscriptionPaidThru(sub.id)
            print "charge successful"
        else:
            # charge failed
            print "failed"

doBilling()


            
        
