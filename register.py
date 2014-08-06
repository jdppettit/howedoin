from flask import *
from flask import request
from dateutil.relativedelta import relativedelta
from password import *

import random
import sys
import traceback

register = Blueprint('register', __name__, template_folder='templates')

def makeAccountID():
    possibleID = random.randint(1, 1000000)
    accountCheck = Account.query.filter_by(id=possibleID).first()

    while accountCheck:
        possibleID = random.randint(1,1000000)
        accountCheck = Account.query.filter_by(id=possibleID).first()

    return possibleID

def checkUsername(username):
    check = User.query.filter_by(username=username).first()
    if check:
        return False
    else:
        return True

def doLogin(username, name, user_id, account_id, email):
    try:
        session['username'] = username
        session['name'] = name
        session['user_id'] = user_id
        session['email'] = email
        session['account_id'] = account_id
    except:
        return False

    return True

def getUserID(record, db):
    db.session.refresh(record)
    return record.id

def getMaxUsers(plan):
    if plan == 0:
        return 3
    elif plan == 1:
        return 5
    elif plan == 2:
        return 10

def doBilling(plan):
    if plan == 0:
        return render_template("dashboard.html")
    elif plan == 1:
        return render_template("billing.html", plan=plan, cost=10)
    elif plan == 2:
        return render_template("billing.html", plan=plan, cost=25)

@register.route('/register', methods=['GET','POST'])
def registerEndpoint():
    try:
        if request.method == "GET":
            try:
                if session['logged_in']:
                    return render_template("dashboard.html", error="You are already registered and logged in.")
                else:
                    # if no logged_in var
                    return render_template("register.html")
            except:
                # if session vars not found (not logged in)
                return render_template("register.html")
        elif request.method == "POST":
            if request.form['username'] and request.form['name'] and request.form['email'] and request.form['password'] and request.form['passwordconfirm'] and request.form['plan']:
                if request.form['plan'] == 1:
                    # if plan is free, don't do billing, paidthru is forever
                    if request.form['company_name']:
                        # if company_name is there, use it
                        if request.form['password'] == request.form['passwordconfirm']:
                            # if the passwords match proceed
                            accountID = makeAccountID()
                            newAccount = Account(accountID, request.form['company_name'], request.form['plan'], "2999-12-31 23:59:59", 1, 3)

                            encryptedPassword = hashPassword(request.form['password'])
                            usernameCheck = checkUsername(request.form['username'])
                            if usernameCheck:
                                # If this returns true, username is unique, proceed
                                newUser = User(accountID, request.form['name'], request.form['username'], encryptedPassword, request.form['email'], 1)
                                db.session.add(newAccount)
                                db.session.add(newUser)
                                db.session.commit()
                                user_id = getUserID(newUser, db)
                                doLogin(request.form['username'], request.form['name'], user_id, account_id, request.form['email'])
                                return render_template("dashboard.html")
                            else:
                                # if false, make them pick a new username
                                return render_template("register.html", company_name=request.form['company_name'], username=request.form['username'], name=request.form['name'], plan=request.form['plan'], email=request.form['email'], error="Sorry, that username is taken. Can you pick another?")
 
                        else:
                            # if not, tell them they messed up
                            return render_template("register.html", company_name=request.form['company_name'], username=request.form['username'], name=request.form['name'], plan=request.form['plan'], email=request.form['email'], error="The passwords you entered didn't match, please try again, thanks!")
                    else:
                        if request.form['password'] == request.form['passwordconfirm']:
                            accountID = makeAccountID()
                            newAccount = Account(accountID, "", request.form['plan'], "2999-12-31 23:59:59", 1, 3)

                            encryptedPassword = hashPassword(request.form['password'])
                            usernameCheck = checkUsername(request.form['username'])
                            if usernameCheck:
                                newUser = User(accountID, request.form['name'], request.form['username'], encryptedPassword, request.form['email'], 1)
                                db.session.add(newAccount)
                                db.session.add(newUser)
                                db.session.commit()
                                user_id = getUserID(newUser, db)
                                doLogin(request.form['username'], request.form['name'], user_id, account_id, request.form['email'])
                                return render_template("dashboard.html")
                            else:
                                return render_template("register.html", company_name=request.form['company_name'], username=request.form['username'], name=request.form['name'], plan=request.form['plan'], email=request.form['email'], error="Sorry, that username is taken. Can you pick another?")
                        else:
                            return render_template("register.html", company_name=request.form['company_name'], username=request.form['username'], name=request.form['name'], plan=request.form['plan'], email=request.form['email'], error="The passwords you entered didn't match, please try again, thanks!")
                        # if its not, provide empty string
                else:
                    # do billing, paidthru should be one month from now
                    if request.form['company_name']:
                        # if company name us it
                        if request.form['password'] == request.form['passwordconfirm']:
                            accountID = makeAccountID()
                            goodThru = datetime.datetime.now() + relativedelta(days=1)
                            maxUsers = getMaxUsers(request.form['plan'])
                            newAccount = Account(accoundID, request.form['company_name'], request.form['plan'],
                            goodThru, 0, maxUsers)

                            encryptedPassword = hashPassword(request.form['password'])
                            usernameCheck = checkUsername(request.form['username'])
                            if usernameCheck:
                                newUser = User(accountID, reuqest.form['name'], request.form['username'],
                                encryptedPassword, request.form['email'], 0)
                                db.session.add(newAccount)
                                db.session.add(newUser)
                                db.session.commit()
                                user_id = getUserID(newUser, db)
                                doLogin(request.form['username'], request.form['name'], user_id, account_id,
                                request.form['email'])
                                doBilling(request.form['plan'])
                            else:
                                return render_template("register.html", company_name=request.form['company_name'],
                                username=request.form['username'], name=request.form['name'], plan=request.form['plan'],
                                email=request.form['email'], error="Sorry, that username is taken. Can you pick another?")
                        else:
                            return render_template("register.html", company_name=request.form['company_name'],
                            username=request.form['username'], name=request.form['name'], plan=request.form['plan'],
                            email=request.form['email'], error="The passwords you entered didn't match, please try again, thanks!")
                    else:
                        # if not use empty string
                        if request.form['password'] == request.form['passwordconfirm']:
                            accountID = makeAccountID()
                            goodThru = datetime.datetime.now() + relativedelta(days=1)
                            maxUsers = getMaxUsers(request.form['plan'])
                            newAccount = Account(accoundID, "", request.form['plan'],
                            goodThru, 0, maxUsers)

                            encryptedPassword = hashPassword(request.form['password'])
                            usernameCheck = checkUsername(request.form['username'])
                            if usernameCheck:
                                newUser = User(accountID, reuqest.form['name'], request.form['username'],
                                encryptedPassword, request.form['email'], 0)
                                db.session.add(newAccount)
                                db.session.add(newUser)
                                db.session.commit()
                                user_id = getUserID(newUser, db)
                                doLogin(request.form['username'], request.form['name'], user_id, account_id,
                                request.form['email'])
                                doBilling(request.form['plan'])
                            else:
                                return render_template("register.html", company_name=request.form['company_name'],
                                username=request.form['username'], name=request.form['name'], plan=request.form['plan'],
                                email=request.form['email'], error="Sorry, that username is taken. Can you pick another?")
                        else:
                            return render_template("register.html", company_name=request.form['company_name'],
                            username=request.form['username'], name=request.form['name'], plan=request.form['plan'],
                            email=request.form['email'], error="The passwords you entered didn't match, please try again, thanks!")
 
            else:
                return render_template("register.html", error="Please fill out all of the required fields.")
            # do all the registration stuff
            # if not on free plan, pass to billing
            # if on free plan, redirect to dashboard
    except Exception, e:
        print e
        traceback.print_exc(file=sys.stdout)
        abort(404)
