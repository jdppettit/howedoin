from flask import *
from models import db
from flask.ext.mail import *

mail = Mail()

def sendWelcome(email_address, account_id):
    return 1

def sendPaymentFailed(email_address, amount, invoice_id):
    msg = Message("Howedoin Renewal Failed", sender="donotreply@howedo.in", recipients = [email_address])
    msg.html = render_template("email_payment_failed.html", invoice_id=invoice_id, amount=amount)
    try:
        mail.send(msg)
    except:
        pass

def sendCreateNewUser(email_address, activation_code, account_id, user_id, name):
    msg = Message("You have been invited to Howedoin", sender = "donotreply@howedo.in", recipients = [email_address])
    msg.html = render_template("email_create_new_user.html", activation_code=activation_code, user_id=user_id,
    account_id=account_id, name=name)
    try:
        mail.send(msg) 
    except:
        pass

def sendForgotPassword(email_address, token):
    msg = Message("Howedoin Password Reset", sender="donotreply@howedo.in", recipients = [email_address])
    msg.html = render_template("email_forgot_password.html", token=token)
    # To keep things from failing if the email isn't formatted right
    try:
        mail.send(msg)
    except:
        pass


