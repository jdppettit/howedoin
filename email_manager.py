from flask import *
from models import db
from flask.ext.mail import *

mail = Mail()

def sendWelcome(email_address, account_id):
    return 1

def sendCreateNewUser(email_address, activation_code, account_id, user_id):
    return 1

def sendForgotPassword(email_address, token, account_id, user_id):
    return 1


