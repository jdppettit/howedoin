from flask import *
from models import db, User, Account, Team
from functions import *

user = Blueprint("user", __name__, template_folder="templates")

def getAllUsers(account_id):
    users = User.query.filter_by(account_id=account_id).all()
    return users

def getAllTeams(account_id):
    teams = Team.query.filter_by(account_id=account_id).all()
    return teams

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
            else:
                return render_template("dashboard_user_create.html", error="All fields must be completed.")
    else:
        return notLoggedIn()
