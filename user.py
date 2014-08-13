from flask import *
from models import db, User, Account, Team
from functions import *
from email_manager import *

import string
import random

user = Blueprint("user", __name__, template_folder="templates")

def getAllUsers(account_id):
    users = User.query.filter_by(account_id=account_id).all()
    return users

def getAllTeams(account_id):
    teams = Team.query.filter_by(account_id=account_id).all()
    return teams

def getActivationURL(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def makeUser(account_id, name, username, email, active, activation_link):
    password = getActivationURL(25)
    newUser = User(account_id, name, username, password, email, "", activation_link)
    db.session.add(newUser)
    db.session.commit()
    db.session.refresh(newUser)
    return newUser.id

@user.route('/dashboard/user/')
def viewUsers():
    resp = checkLogin()
    if resp:
        allUsers = getAllUsers(session['account_id'])
        return render_template("dashboard_user_view.html", users=allUsers)
    else:
        return notLoggedIn()

@user.route('/dashboard/user/create', methods=['POST','GET'])
def createUser():
    resp = checkLogin()
    if resp:    
        if request.method == "GET":
            teams = getAllTeams(session['account_id'])
            return render_template("dashboard_user_create.html", teams=teams)
        elif request.method == "POST":
            if request.form['name'] and request.form['email']:
                return "Poop"
                user_id = makeUser(session['account_id'], request.form['name'], request.form['username'], request.form['email'], 0, getActivationURL(10))
                # do the db stuff
                
                # get the activation token

                # write the activation token to the db

                # send the email
            else:
                return render_template("dashboard_user_create.html", error="All fields must be completed.")
    else:
        return notLoggedIn()
