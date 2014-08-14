from flask import *
from models import db, User, Account, Team
from functions import *
from email_manager import *
from password import *

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
    newUser = User(account_id, name, username, password, email, 0, activation_link)
    db.session.add(newUser)
    db.session.commit()
    db.session.refresh(newUser)
    return newUser.id

def checkToken(token):
    user = User.query.filter_by(activation_link=token).first()
    if user:
        return True, user
    else:
        return False, False

def updateActivatedUser(password, token):
    user = User.query.filter_by(activation_link=token).first()
    user.password = password
    user.active = 1
    db.session.commit()
    return user

@user.route('/dashboard/user/')
def viewUsers():
    resp = checkLogin()
    if resp:
        allUsers = getAllUsers(session['account_id'])
        return render_template("dashboard_user_view.html", users=allUsers)
    else:
        return notLoggedIn()

@user.route('/user/activate/<token>', methods=['POST','GET'])
def activateUser(token):
    if token:
        res, User = checkToken(token)
        if res:
            if request.method == "GET":
            # token is good, lets do the needful
                return render_template("activate_user.html", token=token)
            elif request.method == "POST":
                if request.form['password'] == request.form['passwordconfirm']:
                    newPassword = hashPassword(request.form['password'])
                    user = updateActivatedUser(newPassword, token)
                    doLogin(user)
                    return redirect('/dashboard')
                else:
                    return render_template("activate_user.html", token=token, error="Your passwords do not match. Please try again!")
        else:
            return render_template("done.html", error="That token does not match a user.")
    else:
        return render_template("index.html")

@user.route('/dashboard/user/create', methods=['POST','GET'])
def createUser():
    resp = checkLogin()
    if resp:    
        if request.method == "GET":
            teams = getAllTeams(session['account_id'])
            return render_template("dashboard_user_create.html", teams=teams)
        elif request.method == "POST":
            if request.form['name'] and request.form['email'] and request.form['username']:
                activation_code = getActivationURL(10)
                user_id = makeUser(session['account_id'], request.form['name'], request.form['username'],
                request.form['email'], 0, activation_code)
                sendCreateNewUser(request.form['email'], activation_code, session['account_id'], user_id, request.form['name'])
                return render_template("dashboard_user_view.html", message="Activation email sent to this user.")
            else:
                return render_template("dashboard_user_create.html", error="All fields must be completed.")
    else:
        return notLoggedIn()
