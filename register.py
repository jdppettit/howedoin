from flask import *
from dateutil.relativedelta import relativedelta
from password import *

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

@register.route('/register', methods=['POST','GET'])
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
                            newAccount = Account(accountID, request.form['company_name'], request.form['plan'], "2999-12-31
                            23:59:59", 1, 3)

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

                            encryptedPAssword = hashPassword(request.form['password'])
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
                        print "test"
                    else:
                        print "test"
                        # if not use empty string
            else:
                return render_template("register.html", error="Please fill out all of the required fields.")
            # do all the registration stuff
            # if not on free plan, pass to billing
            # if on free plan, redirect to dashboard
    except:
        abort(404)
