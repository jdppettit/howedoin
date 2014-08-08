from flask import *
from models import db, Account
from dateutil.relativedelta import relativedelta
from datetime import datetime

import stripe

stripe.api_key = "sk_test_XyBItKO0iLZssC4uqGCLOOWd"

billing = Blueprint('billing', __name__, template_folder='templates')

def updatePaidThru(account):
    newExpiry = datetime.now() + relativedelta(months=1)
    account.paid_thru = newExpiry
    db.session.commit()

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
                email=session['email']
            )

            account = Account.query.filter_by(id=request.form['account_id']).first()
            account.stripe_customer = customer
            db.session.commit()

            return render_template("done.html")

        else:
            return render_template("billing.html", error="Something went wrong, your card has not been billed. Please try again.") # need to add in the variables again
    else:
        abort(404)

@billing.route('/billing/hooks', methods=['POST'])
def hooks():
    print "this checks for hooks"

