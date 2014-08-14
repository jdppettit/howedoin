from flask import *
from models import db
from flask.ext.mail import *

mail = Mail()

def sendWelcome(email_address, account_id):
    return 1

def sendCreateNewUser(email_address, activation_code, account_id, user_id, name):
    msg = Message("You have been invited to Howedoin", sender = "donotreply@howedo.in", recipients = [email_address])
    msg.html = render_template("email_create_new_user.html", activation_code=activation_code, user_id=user_id,
    account_id=account_id, name=name)
    mail.send(msg) 

def sendForgotPassword(email_address, token, account_id, user_id):
    return 1


