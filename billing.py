from flask import *
from models import db, Account, Invoice, InvoiceItem, Payment, Subscription
from dateutil.relativedelta import relativedelta
from datetime import datetime
from functions import *
from email_manager import *
from gatekeeper import *
from account import *
import register

import stripe
import pprint

stripe.api_key = "sk_test_XyBItKO0iLZssC4uqGCLOOWd"

billing = Blueprint('billing', __name__, template_folder='templates')

def updatePaidThru(account):
    newExpiry = datetime.now() + relativedelta(months=1)
    account.paid_thru = newExpiry
    db.session.commit()

def updateAccountPlanID(account_id, plan_id):
    account = Account.query.filter_by(id=account_id).first()
    account.plan_id = plan_id
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

def makePayment(account_id, invoice_id, credit, debit, transaction_id, date=datetime.now(), switch=0):
    if switch == 0:
        newPayment = Payment(account_id, invoice_id, credit, debit, transaction_id, date)
        db.session.add(newPayment)
        db.session.commit()
        db.session.refresh(newPayment)
        invoice = Invoice.query.filter_by(id=invoice_id).first()
        invoice.paid = 1
        invoice.payment_id = newPayment.id
        db.session.commit()
        return 1
    elif switch == 1:
        newPayment = Payment(account_id, invoice_id, credit, debit, transaction_id, date)
        db.session.add(newPayment)
        db.session.commit()
        db.session.refresh(newPayment)
        return newPayment.id

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
        total = total + 25.00
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

def getProrationUsers(account_id, users_added):
    subscription = Subscription.query.filter_by(account_id=account_id).first()
    now = datetime.now()
    diff = subscription.paid_thru - now
    diff_days = diff.days
    
    monthly_cost = subscription.cost_per_add * users_added
    daily_cost = subscription.cost_per_add / 30
    prorated_cost = daily_cost * diff_days * users_added
    return prorated_cost, monthly_cost

def cancelSubscription(account_id):
    subscription = Subscription.query.filter_by(account_id=account_id).first()
    subscription.cancelled = 1
    db.session.commit()

def makeRefund(stripe_customer, charge_id, amount):
    charge = stripe.Charge.retrieve(charge_id)
    striped_amount = amount * 100
    striped_amount = int(striped_amount)
    try:
        refund = charge.refunds.create(
                    amount=striped_amount
                )
    except Exception, e:
        print "Shit broke: %s" % str(e)
        print "Tried to refund: %s " % str(amount)
        return False
    return True
    

def makeCharge(stripe_customer, cost, description):
    try:
        cost = cost * 100
        cost = int(cost)
        charge = stripe.Charge.create(
            amount = cost,
            currency = "usd",
            customer = stripe_customer,
            description = description)
        return True, charge
    except stripe.CardError, e:
        return False

def getStripeCustomer(account_id):
    account = Account.query.filter_by(id=account_id).first()
    return account.stripe_customer

def updateSubscription(account_id, cost, max_users):
    subscription = Subscription.query.filter_by(account_id=account_id).first()
    subscription.total_monthly = subscription.total_monthly + cost
    subscription.extra_users = subscription.extra_users + int(max_users)
    db.session.commit()
    return 1

def updateAccountMaxUsers(account_id, max_users, switch=0):
    if switch == 0:
        account = Account.query.filter_by(id=account_id).first()
        account.max_users = int(account.max_users) + int(max_users)
        db.session.commit()
        return 1
    else:
        account = Account.query.filter_by(id=account_id).first()
        account.max_users = int(max_users)
        db.session.commit()
        return 1

def getAllSubscriptions():
    subscriptions = Subscription.query.filter_by(id>0).all()
    return subscriptions

def getBillableSubscriptions():
    now = datetime.now()
    subscriptions = Subscription.query.filter(Subscription.paid_thru<=now).filter_by(cancelled!=1).all()
    return subscriptions

def getBillableAccounts():
    now = datetime.datetime.now()
    needsBilling = []
    for subscription in subscriptions:
        if subscription.paid_thru < now:
            needsBilling.append(subscription.account_id)
    return needsBilling
            
def updateSubscriptionPaidThru(subscription_id):
    subscription = Subscription.query.filter_by(id=subscription_id).first()
    subscription.paid_thru = datetime.now() + relativedelta(months=1)
    db.session.commit()

def makeLastInvoicePaid(account_id, invoice_total, payment_id):
    lastInvoice = Invoice.query.filter_by(account_id=account_id).filter_by(total=invoice_total).filter_by(paid=0).first()
    lastInvoice.paid = 1
    lastInvoice.payment_id = payment_id
    db.session.commit()

def getPlanName(plan_id):
    plan_id = int(plan_id)
    if plan_id == 0:
        return "Howedoin Free"
    elif plan_id == 1:
        return "Howedoin Business Plan"
    elif plan_id == 2:
        return "Howedoin Enterprise Plan"

def retryBilling():
    retryAccounts = Account.query.filter_by(retry_billing=1).all()

    for account in retryAccounts:
        sub = Subscription.query.filter_by(account_id=account.id).filter_by(cancelled!=1).first()
        stripe_customer = account.stripe_customer
        invoice_total = sub.total_monthly
        
        res, charge = makeCharge(stripe_customer, invoice_total, "Howedoin - Monthly Recurring")

        if res:
            payment_id = makePayment(account.id, invoice_id, invoice_total, 0, charge['id'], switch=1)
            markLastInvoicePaid(account.id, invoice_total, payment_id)
            updateSubscriptionPaidThru(sub.id)
            print "charge successful"
        else:
            # charge failed
            try:
                sendPaymentFailed(account.billing_email, sub.total_monthly, invoice_id)
            except:
                pass
            account.retry_billing = 0
            account.cancel = 1
            db.session.commit()
            # set retry billing flag to 1
            # bump paid through 1 week
            print "failed"


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
        
        invoice_total = sub.total_monthly

        res, charge = makeCharge(stripe_customer, invoice_total, "Howedoin - Monthly Recurring")

        if res:
            makePayment(account.id, invoice_id, invoice_total, 0, charge['id'])
            updateSubscriptionPaidThru(sub.id)
            print "charge successful"
        else:
            # charge failed
            try:
                sendPaymentFailed(account.billing_email, sub.total_monthly, invoice_id)
            except:
                pass
            account.retry_billing = 1
            account.paid_thru = datetime.datetime.now() + relativedelta(weeks=1)
            db.session.commit()
            # set retry billing flag to 1
            # bump paid through 1 week
            print "failed"

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
            makePayment(account_id, invoice_id, getCost(request.form['plan']), 0.00, charge['id'])
            account.plan_id = request.form['plan']
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
        if session['account_id'] and request.form['confirm']:
            # this needs to pass the subscription ID back
            you = Account.query.filter_by(id=session['account_id']).first()
            cancelSubscription(you.id)
            return render_template("billing_cancelled.html")
        else:
            return render_template("login.html", error="You must be logged in to do this.")

@billing.route('/billing/addusers', methods=['POST','GET'])
def addUsers():
    if request.method == "GET":
        return render_template("billing_add_users.html")
    elif request.method == "POST":
        # Get prorated amount
        cost, monthly_cost = getProrationUsers(session['account_id'], int(request.form['users_to_add']))

        # Make invoice
        invoice_id = makeInvoice(session['account_id'], cost, 0)

        # Make line item
        makeInvoiceLineItem(session['account_id'], invoice_id, "Additional %s User(s)" %
        str(request.form['users_to_add']), debit=cost)
        
        # Get stripe customer
        stripe_customer = getStripeCustomer(session['account_id'])

        # Make charge
        result, charge = makeCharge(stripe_customer, cost, "Additional %s User(s)" % str(request.form['users_to_add']))

        if result:
            # proceed, card accepted
            makePayment(session['account_id'], invoice_id, cost, 0, charge['id'])
            updateSubscription(session['account_id'], monthly_cost, request.form['users_to_add'])
            updateAccountMaxUsers(session['account_id'], request.form['users_to_add'])
            return render_template("done.html", message="Complete.")
        else:
            return render_template("done.html", error="Your card was declined.")

@billing.route('/billing/edit', methods=['POST','GET'])
def editBilling():
    if request.method == "GET":
        return render_template("billing_edit.html")
    elif request.method == "POST":
        print "does the thing"

@billing.route('/admin/billing/dobilling/initial')
def adminDoBilling():
    doBilling()
    return "Done."

@billing.route('/admin/billing/dobilling/retry')
def adminRetryBilling():
    retryBilling()
    return "Done."

@billing.route('/dashboard/billing/invoice/<invoice_id>')
def getInvoice(invoice_id):
    res = checkLogin()
    if res:
        invoice = Invoice.query.filter_by(id=invoice_id).first()
        invoice_lines = InvoiceItem.query.filter_by(invoice_id=invoice.id).all()
        return render_template("dashboard_account_billing_invoice.html", invoice=invoice, invoice_lines=invoice_lines)
    else:
        return notLoggedIn()

@billing.route('/dashboard/billing/change', methods=['POST','GET'])
@billing.route('/billing/change', methods=['POST','GET'])
def changeBilling(account_id = 0):
    # This will allow the user to modify their billing plan
    res = checkLogin()
    if res:
        gatekeeper = accountGatekeeper(session['user_id'], session['account_id'], 3)
        if gatekeeper:
            if request.method == "GET":
                account = Account.query.filter_by(id=session['account_id']).first()
                plan_id = account.plan_id
                plan_name = getPlanName(plan_id)
                currentUsers = getCurrentUsers(account.id)
                maxUsers = getMaxUsers(account.id)
                paid_thru = getPaidThru(account.id)
                monthly_cost = getMonthlyCost(account.id)
                subscriptions = Subscription.query.filter_by(account_id=account.id).all()
                pending_change = False
                new_subscription = 0
                if len(subscriptions) > 1:
                    # There is a change pending
                    pending_change = True
                    for subscription in subscriptions:
                        if subscription.cancelled != 1:
                            new_subscription = subscription.plan
                return render_template("dashboard_account_billing_change.html", plan_id=plan_id, plan_name=plan_name,
                current_users=currentUsers, max_users=maxUsers, monthly_cost=monthly_cost, paid_thru=paid_thru,
                pending_change=pending_change, new_subscription=new_subscription)
            elif request.method == "POST":
                account = Account.query.filter_by(id=session['account_id']).first()
                new_plan = request.form['plan']
                new_plan = int(new_plan)
                if new_plan == account.plan_id:
                    return redirect('/dashboard/account/billing')
                    # NEW STUFF #
                
                # Get current subscription
                current_subscription = Subscription.query.filter_by(id=account.subscription_id).first()

                # Get the number of days left until sub is over
                now = datetime.now()
                paid_thru = current_subscription.paid_thru
            
                remaining_days = paid_thru - now
                remaining_days = remaining_days.days

                # Get monthly cost / extra user cost
                monthly_cost = 0.00
                extra_user_cost = 0.00

                if account.plan_id == 1:
                    monthly_cost = 10.00
                    extra_user_cost = 3.00
                elif account.plan_id == 2:
                    monthly_cost = 25.00
                    extra_user_cost = 2.50

                # Calculate total monthly cost
                total_monthly_cost = 0.00

                total_monthly_cost += total_monthly_cost + monthly_cost

                extra_user_holder = 0.00
                extra_user_holder = extra_user_cost * current_subscription.extra_users

                total_monthly_cost += extra_user_holder

                # Calculate the daily rate
                daily_rate = total_monthly_cost / 30

                # Calculate the funds not yet used
                unused_funds = daily_rate * remaining_days
                
                # Make new subscription
                if new_plan == 0:
                    new_subscription_id = makeSubscription(account.id, request.form['plan'], 0)
                else:
                    new_subscription_id = makeSubscription(account.id, request.form['plan'],
                    current_subscription.extra_users)

                new_subscription = Subscription.query.filter_by(id=new_subscription_id).first()
                
#                if new_plan == 1 or new_plan == 2 and account.plan_id == 0:
                    # This is an upgrade, must be handled differently
#                    return 1

                if new_subscription.total_monthly > unused_funds:
                    amount_to_charge = new_subscription.total_monthly - unused_funds 
                    new_invoice_id = makeInvoice(account.id, new_subscription.total_monthly, 0)
                    makeInvoiceLineItem(account.id, new_invoice_id, getPlanName(new_subscription.plan),
                    debit=new_subscription.total_monthly)
                    new_plan_id = int(new_subscription.plan)
                    if new_subscription.extra_users > 0:
                        if new_plan_id == 1:
                            extra_user_cost = new_subscription.extra_users * 3.00
                            updateAccountMaxUsers(account.id, 5 + new_subscription.extra_users, switch=1)
                        if new_plan_id == 2:
                            extra_user_cost = new_subscription.extra_users * 2.50
                            updateAccountMaxUsers(account.id, 10 + new_subscription.extra_users, switch=1)
                        makeInvoiceLineItem(account.id, new_invoice_id, "Extra Users", debit=extra_user_cost)
                    else:
                        if new_plan_id == 1:
                            updateAccountMaxUsers(account.id, 5, switch=1)
                        elif new_plan_id == 2:
                            updateAccountMaxUsers(account.id, 10, switch=1)
                    makeInvoiceLineItem(account.id, new_invoice_id, "Prorated Amount", credit=unused_funds)
                    db.session.delete(current_subscription)
                    charge_amount = new_subscription.total_monthly - unused_funds
                    resp, charge = makeCharge(account.stripe_customer, charge_amount, "Change to Howedoin Plan")
                    if resp:
                        # Charge successful
                        updatePaidThru(account)
                        updateSubscriptionID(account.id, new_subscription_id)
                        new_payment_id = makePayment(account.id, new_invoice_id, 0, charge_amount + unused_funds, charge.id)
                        updateIsCurrent(account.id)
                        updateAccountPlanID(account.id, new_plan_id)
                        db.session.commit()
                        return redirect('/dashboard/account/billing')
                    else:
                        # return a template to try again
                        return "The payment failed"
                else:
                    if new_plan == 0:
                        refund_due = unused_funds
                    else:
                        refund_due = unused_funds - new_subscription.total_monthly
                    # Proceed with refund logic
                    last_invoice = Invoice.query.filter_by(account_id=account.id).filter_by(paid=1).filter_by(refunded=0).filter(Invoice.total>=refund_due).order_by(Invoice.id.desc()).limit(1).first()
                    invoice_payment = Payment.query.filter_by(id=last_invoice.payment_id).first()
                    stripe_response = makeRefund(account.stripe_customer, invoice_payment.transaction_id, refund_due)
                    if stripe_response == True:
                        invoice_payment.refunded = 1
                        db.session.commit()
                        new_invoice_id = makeInvoice(account.id, new_subscription.total_monthly, 0)
                        makeInvoiceLineItem(account.id, new_invoice_id, getPlanName(new_subscription.plan),
                        debit=new_subscription.total_monthly)
                        new_plan_id = int(new_subscription.plan)
                        if new_subscription.extra_users > 0:
                            if new_plan_id == 1:
                                extra_user_cost = new_subscription.extra_users * 3.00
                                updateAccountMaxUsers(account.id, 5 + new_subscription.extra_users, switch=1)
                            elif new_plan_id == 2:
                                extra_user_cost = new_subscription.extra_users * 2.50
                                updateAccountMaxUsers(account.id, 10 + new_subscription.extra_users, switch=1)
                            makeInvoiceLineItem(account.id, new_invoice_id, "Extra Users", debit=extra_user_cost)
                        else:
                            if new_plan_id == 1:
                                updateAccountMaxUsers(account.id, 5, switch=1)
                            elif new_plan_id == 2:
                                updateAccountMaxUsers(account.id, 10, switch=1)
                        makeInvoiceLineItem(account.id, new_invoice_id, "Prorated Amount", credit=refund_due)
                        db.session.delete(current_subscription)
                        updatePaidThru(account)
                        updateSubscriptionID(account.id, new_subscription_id)
                        new_payment_id = makePayment(account.id, new_invoice_id, 0, 0.00, "CREDIT")
                        updateIsCurrent(account.id)
                        updateAccountPlanID(account.id, new_plan_id)
                        db.session.commit()
                        return redirect('/dashboard/account/billing')
        else:
            return render_template("permission_denied.html")
    else:
        return notLoggedIn()

@billing.route('/billing/upgrade', methods=['POST','GET'])
def upgradeBilling():
    res = checkLogin()
    if res:
        gatekeeper = accountGatekeeper(session['user_id'], session['account_id'], 3)
        if gatekeeper:
            if request.method == "GET":
                return render_template("upgrade.html")
            elif request.method == "POST":
                new_plan = request.form['plan']
                account = Account.query.filter_by(id=session['account_id']).first()
                subscription = Subscription.query.filter_by(account_id=account.id).filter_by(plan=0).first()
                db.session.delete(subscription)
                db.session.commit()
                return register.doBilling(new_plan, account.company_name, account.id, account.billing_email)
        else:
            return render_template("permission_denied.html")
    else:
        return notLoggedIn()
