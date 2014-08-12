from functions import *
from models import *
from datetime import *
from billing import *

import stripe

def getAllSubscriptions():
    subscriptions = Subscription.query.filter_by(id>0).all()
    return subscriptions

def getBillableAccounts(subscriptions):
    now = datetime.datetime.now()
    needsBilling = []
    for subscription in subscriptions:
        if subscription.paid_thru < now:
            needsBilling.append(subscription.account_id)
    return needsBilling
            
def makeInvoices(needsBilling):
    
def doBilling():
    allSubs = getAllSubscriptions()
    now = datetime.datetime.now()
    needsBilling = getBillableAccounts()
         
            
        
