from flask import *
from models import db, Subscription, Inovice, InvoiceItem, Account, Payment
from functions import *

account = Blueprint('account', __name__, template_folder="templates")

@account.route('/dashboard/account/billing')
def accountBilling():
    resp = checkLogin()
    if resp:
        
    else:
        return notLoggedIn()
