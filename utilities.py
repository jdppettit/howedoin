from flask import *

utility = Blueprint("utility", __name__, template_folder='templates')

@utility.route('/admin/utility/subscription-cycle')
def subCycle():
    # Grab all accounts
    # For each account, grab subscriptions
    
    # If there is more than one subscription, and one is cancelled, and the cancelled subscription's paid thru date is
    # past, remove that subscription
    
    # Make the other subscription active 
    # Update account with newest subscription ID

    accounts = Account.query.filter_by(id>=1).all()
    for account in accounts:
        subscriptions = Subscription.query.filter_by(account_id=account.id).all()
        if len(subscriptions) > 1:
            
