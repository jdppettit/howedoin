from flask import *
from models import db, User, Account, Team
from functions import *
from email_manager import *
from password import *
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pprint import pprint
from gatekeeper import *

import string
import random

user = Blueprint("user", __name__, template_folder="templates")

def removeAdminStatus(user_id, account_id):
    permission = Permission.query.filter_by(user_id=user_id).filter_by(account_id=account_id).filter_by(permission_type=99).first()
    db.session.delete(permission)
    db.session.commit()

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

def checkExistingReset(activation):
    check = User.query.filter_by(password_reset_link=activation).first()
    if check:
        return False
    else:
        return True

def validateReset(activation):
    check = User.query.filter_by(password_reset_link=activation).first()
    now = datetime.now()
    if check:
        if now > check.password_reset_expire:
            # If its found but expired
            return False, 0
        else:
            return True, check
    else:
        return False, 0

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

def translatePermission(permission):
    if permission == "add":
        return 1
    elif permission == "remove":
        return 2
    elif permission == "modify":
        return 3
    elif permission == "view":
        return 4
    elif permission == "all":
        return 5

def checkAndMakePermissions(account_id, user_id, permission_type, permission, team_id=0):
    translated_permission = translatePermission(permission)
    if team_id != 0:
        check = Permission.query.filter_by(account_id=account_id).filter_by(user_id=user_id).filter_by(team_id=team_id).filter_by(permission_type=permission_type).filter_by(permission=translated_permission).first()
        if check:
            # Permission already exists
            return 1
        else:
            # doesn't exist, make it
            perm = Permission(account_id, user_id, permission_type, translated_permission, team_id=team_id)
            db.session.add(perm)
            db.session.commit()
            return 1
    else:
        check = Permission.query.filter_by(account_id=account_id).filter_by(user_id=user_id).filter_by(permission_type=permission_type).filter_by(permission=translated_permission).first()
        if check:
            # permission there
            return 1
        else:
            perm = Permission(account_id, user_id, permission_type, translated_permission)
            db.session.add(perm)
            db.session.commit()
            return 1

'''
States
-----
1 = Is present in list, should be added if not present in permissions table
2 = Is not present in list, should be removed if present in permissions table
'''

def addRemovePermissions(account_id, user_id, permission_type, permission, state, team_id=0):
    translated_permission = translatePermission(permission)
    if team_id != 0:
        permission = Permission.query.filter_by(account_id=account_id).filter_by(user_id=user_id).filter_by(permission_type=permission_type).filter_by(permission=translated_permission).filter_by(team_id=team_id).first()
    else:
        permission = Permission.query.filter_by(account_id=account_id).filter_by(user_id=user_id).filter_by(permission_type=permission_type).filter_by(permission=translated_permission).first()

    if state == 1 and not permission:
        # this means the permission was checked, but is not present, make it
        if team_id != 0:
            newPermission = Permission(account_id, user_id, permission_type, translated_permission, team_id=team_id)
            db.session.add(newPermission)
            db.session.commit()
            return 1
        else:
            newPermission = Permission(account_id, user_id, permission_type, translated_permission)
            db.session.add(newPermission)
            db.session.commit()
            return 1
    if state == 2 and permission:
        # this means the permission was not checked, but it exists, remove it
        db.session.delete(permission)
        db.session.commit()
        return 1

@user.route('/forgot/<token>', methods=['GET','POST'])
def forgotHandler(token):
    if request.method == "GET":
        resp, user = validateReset(token)
        if resp:
            return render_template("reset.html", token=token, user_id=user.id, accound_id=user.account_id)
        else:
            return render_template("forgot.html", error="That code either doesn't exist or has expired. Try again.")
    elif request.method == "POST":
        if request.form.has_key('username') and request.form.has_key('email') and request.form.has_key('password') and request.form.has_key('passwordconfirm') and request.form.has_key('user_id') and request.form.has_key('account_id'):
            if request.form['password'] == request.form['passwordconfirm']:
                user = User.query.filter_by(username=request.form['username']).filter_by(email=request.form['email']).filter_by(password_reset_link=token).first()
                user.password_reset_link = ""
                user.password_reset_expire = "2999-12-31 23:59:59"
                newPassword = ""
                newPassword = hashPassword(request.form['password'])
                user.password = newPassword
                db.session.commit()
                return render_template("login.html", username=user.username, message="Password reset successfully.")
            else:
                resp, user = validateReset(token)
                return render_template("reset.html", token=token, user_id=user.id, account_id=user.account_id,
                error="Your passwords did not match, try again.")
        else:
            return render_template("forgot.html", error="Something went wrong, try again.")

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
                sendForgotPassword(user.email, resetLink)
            except:
                pass
            return render_template("forgot.html", message="If an account matched those credentials you should get an email momentarily.")

@user.route('/dashboard/user/')
def viewUsers():
    resp = checkLogin()
    if resp:
        gatekeeper = accountGatekeeper(session['user_id'], session['account_id'], 4)
        if gatekeeper:
            allUsers = getAllUsers(session['account_id'])
            return render_template("dashboard_user_view.html", users=allUsers)
        else:
            return render_template("permission_denied.html")
    else:
        return notLoggedIn()

@user.route('/dashboard/user/<user_id>', methods=['POST','GET'])
def editUser(user_id):
    res = checkLogin()
    if res:
        gatekeeper = accountGatekeeper(session['user_id'], session['account_id'], 3)
        if gatekeeper:
            if request.method == "GET":
                user = User.query.filter_by(id=user_id).first()
                teams = Team.query.filter_by(account_id=session['account_id']).all()
                membership = Membership.query.filter_by(account_id=session['account_id']).all()
                iterable = 0
                if len(membership) > 1:
                    iterable = 1
                else:
                    iterable = 0
                account_permissions = Permission.query.filter_by(account_id=session['account_id']).filter_by(user_id=user_id).filter_by(permission_type=2).all()
                team_permissions = Permission.query.filter_by(account_id=session['account_id']).filter_by(user_id=user_id).filter_by(permission_type=1).all()
                is_admin = checkAdmin(user_id, session['account_id'])
                print str(is_admin)
                return render_template("dashboard_user_edit.html", user=user, teams=teams, membership=membership,
                iterable=iterable, account_permissions=account_permissions, team_permissions=team_permissions,
                is_admin=is_admin)
            elif request.method == "POST":
                user = User.query.filter_by(id=user_id).filter_by(account_id=session['account_id']).first()
                teams = Team.query.filter_by(account_id=session['account_id']).all()
                if request.form.has_key('username'):
                    user.username = request.form['username']
                if request.form.has_key('email'):
                    user.email = request.form['email']
                if request.form.has_key('name'):
                    user.name = request.form['name']
                if request.form.has_key('account_permissions'):
                    account_list = request.form.getlist('account_permissions')
                    if "add" not in account_list:
                        addRemovePermissions(user.account_id, user.id, 2, "add", 2)
    
                    if "remove" not in account_list:
                        addRemovePermissions(user.account_id, user.id, 2, "remove", 2)
    
                    if "modify" not in account_list:
                        addRemovePermissions(user.account_id, user.id, 2, "modify", 2)
                    
                    if "view" not in account_list:
                        addRemovePermissions(user.account_id, user.id, 2, "view", 2)
    
                    if "all" not in account_list:
                        addRemovePermissions(user.account_id, user.id, 2, "all", 2)
    
                    for a in request.form.getlist('account_permissions'):
                        addRemovePermissions(user.account_id, user.id, 2, a, 1)
                else:
                    # remove them all
                    addRemovePermissions(user.account_id, user.id, 2, "add", 2)
                    addRemovePermissions(user.account_id, user.id, 2, "remove", 2)
                    addRemovePermissions(user.account_id, user.id, 2, "modify", 2)
                    addRemovePermissions(user.account_id, user.id, 2, "view", 2)
                    addRemovePermissions(user.account_id, user.id, 2, "all", 2)
    
                for team in teams:
                    if request.form.has_key('%s_permissions' % team.team_name):
                        # permissions changed
                        team_list = request.form.getlist('%s_permission' % team.team_name)
                        if "add" not in team_list:
                            addRemovePermissions(user.account_id, user.id, 1, "add", 2, team_id=team.id)
                        if "remove" not in team_list:
                            addRemovePermissions(user.account_id, user.id, 1, "remove", 2, team_id=team.id)
                        if "modify" not in team_list:
                            addRemovePermissions(user.account_id, user.id, 1, "modify", 2, team_id=team.id)
                        if "view" not in team_list:
                            addRemovePermissions(user.account_id, user.id, 1, "view", 2, team_id=team.id)
                        if "all" not in team_list:
                            addRemovePermissions(user.account_id, user.id, 1, "all", 2, team_id=team.id)
                        for a in request.form.getlist('%s_permissions' % team.team_name):
                            addRemovePermissions(user.account_id, user.id, 1, a, 1, team_id=team.id)
                    else:
                        # remove them all
                        addRemovePermissions(user.account_id, user.id, 1, "add", 2, team_id=team.id)
                        addRemovePermissions(user.account_id, user.id, 1, "remove", 2, team_id=team.id)
                        addRemovePermissions(user.account_id, user.id, 1, "modify", 2, team_id=team.id)
                        addRemovePermissions(user.account_id, user.id, 1, "view", 2, team_id=team.id)
                        addRemovePermissions(user.account_id, user.id, 1, "all", 2, team_id=team.id)
    
                db.session.commit()
                return redirect('/dashboard/user')
        else:
            return render_template("permission_denied.html")
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
        gatekeeper = accountGatekeeper(session['user_id'], session['account_id'], 2)
        if gatekeeper:
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
                
                permissions = Permission.query.filter_by(user_id=user_id).filter_by(account_id=session['account_id']).all()
    
                for permission in permissions:
                    db.session.delete(permission)
    
                db.session.delete(user)
                db.session.commit()
                return redirect('/dashboard/user')
        else:
            return render_template("permission_denied.html")
    else:
        return notLoggedIn()

@user.route('/dashboard/user/create', methods=['POST','GET'])
def createUser():
    resp = checkLogin()
    if resp:    
        gatekeeper = accountGatekeeper(session['user_id'], session['account_id'], 1)
        if gatekeeper:
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
                return render_template("permission_denied.html")
    else:
        return notLoggedIn()

@user.route('/dashboard/user/<user_id>/admin')
def toggleAdmin(user_id):
    resp = checkLogin()
    if resp:
        gatekeeper = accountGatekeeper(session['user_id'], session['account_id'], 3)
        if gatekeeper:
            if user_id:
                user = User.query.filter_by(id=user_id).filter_by(account_id=session['account_id']).first()
                currentAdminStatus = checkAdmin(user.id, user.account_id)
                if currentAdminStatus == True:
                    removeAdminStatus(user.id, user.account_id)
                else:
                    makeAdmin(user.id, user.account_id)
                return redirect('/dashboard/user/%s' % str(user_id))
            else:
                return redirect('/dashboard/user/%s' % str(user_id))
        else:
            return render_template("permission_denied.html")
    else:
        return notLoggedIn()
