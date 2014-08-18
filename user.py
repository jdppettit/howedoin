from flask import *
from models import db, User, Account, Team
from functions import *
from email_manager import *
from password import *
from datetime import datetime
from dateutil.relativedelta import relativedelta

import string
import random

user = Blueprint("user", __name__, template_folder="templates")

def getAllUsers(account_id):
    users = User.query.filter_by(account_id=account_id).all()
    return users

def checkMaxUsers(account_id):
    account = Account.query.filter_by(id=account_id).first()
    existing_max = account.max_users
    users = User.query.filter_by(account_id=account_id).all()
    current_users = len(users)
    new_current_users = current_users + 1
    if new_current_users > existing_max:
        return False
    else:
        return True

def checkExistingActivation(activation):
    check = User.query.filter_by(activation_link=activation).first()
    if check:
        return False
    else:
        return True

def checkExistingReset(activation)
    check = User.query.filter_by(password_reset_link=activation).first()
    if check:
        return False
    else:
        return True

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

def addMembership(account_id, user_id, team_id):
    newMembership = Membership(account_id, user_id, team_id, is_admin=0)
    db.session.add(newMembership)
    db.session.commit()

@user.route('/forgot', methods=['GET','POST'])
def forgot():
    if request.method == "GET":
        return render_template("forgot.html")
    elif request.method == "POST":
        if request.form.has_key('username') and request.form.has_key('email'):
            user = User.query.filter_by(username=request.form['username']).filter_by(email=request.form['email']).first()
            resetLink = getActivationURL(10)
            while not checkExistingReset(resetLink):
                resetLink = getActivationURL(10)
            try:
                user.password_reset_link = resetLink
                user.password_reset_expire = datetime.now() + relativedelta(days=1)
                db.session.commit()
            except:
                pass
            return render_template("forgot.html", message="If an account matched those credentials you should get an email momentarily.")

@user.route('/dashboard/user/')
def viewUsers():
    resp = checkLogin()
    if resp:
        allUsers = getAllUsers(session['account_id'])
        return render_template("dashboard_user_view.html", users=allUsers)
    else:
        return notLoggedIn()

@user.route('/dashboard/user/<user_id>', methods=['POST','GET'])
def editUser(user_id):
    res = checkLogin()
    if res:
        if request.method == "GET":
            user = User.query.filter_by(id=user_id).first()
            teams = Team.query.filter_by(account_id=session['account_id']).all()
            membership = Membership.query.filter_by(account_id=session['account_id']).all()
            iterable = 0
            if len(membership) > 1:
                iterable = 1
            else:
                iterable = 0
            return render_template("dashboard_user_edit.html", user=user, teams=teams, membership=membership,
            iterable=iterable)
        elif request.method == "POST":
            user = User.query.filter_by(id=user_id).filter_by(account_id=session['account_id']).first()
            if request.form.has_key('username'):
                user.username = request.form['username']
            if request.form.has_key('email'):
                user.email = request.form['email']
            if request.form.has_key('name'):
                user.name = request.form['name']
            db.session.commit()
            return redirect('/dashboard/user')
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

@user.route('/dashboard/user/delete/<user_id>', methods=['POST','GET'])
def deleteUser(user_id):
    res = checkLogin()
    if res:
        if request.method == "GET":
            return render_template("dashboard_user_delete.html", user_id=user_id)
        elif request.method == "POST":
            user = User.query.filter_by(id=user_id).filter_by(account_id=session['account_id']).first()
            membership = Membership.query.filter_by(user_id=user_id).filter_by(account_id=session['account_id']).all()

            for member in membership:
                db.session.delete(member)
            
            ratings = Rating.query.filter_by(user_id=user_id).filter_by(account_id=session['account_id']).all()

            for rating in ratings:
                db.session.delete(rating)

            db.session.delete(user)
            db.session.commit()
            return redirect('/dashboard/user')
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
            max_user_check = checkMaxUsers(session['account_id'])
            if max_user_check:
                if request.form['name'] and request.form['email'] and request.form['username']:
                    activation_code = getActivationURL(10)
                    while not checkExistingActivation(activation_code):
                        activation_code = getActivationURL(10)
                    user_id = makeUser(session['account_id'], request.form['name'], request.form['username'],
                    request.form['email'], 0, activation_code)
                    if request.form.has_key('teams'):
                        selected_teams = request.form.getlist('teams')
                        for team in selected_teams:
                            addMembership(session['account_id'], user_id, team)
                    sendCreateNewUser(request.form['email'], activation_code, session['account_id'], user_id, request.form['name'])
                    users = getAllUsers(session['account_id'])
                    return render_template("dashboard_user_view.html", message="Activation email sent to this user.",
                    users=users)
                else:
                    return render_template("dashboard_user_create.html", error="All fields must be completed.")
            else:
                return render_template("dashboard_user_view.html", message="You need to add more users to you account!")
    else:
        return notLoggedIn()
