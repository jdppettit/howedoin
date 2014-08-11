from flask import *

dashboard = Blueprint('dashboard', __name__, template_folder='templates')

def checkLogin():
    try:
        if session['username']:
            return True
    except:
        return False

def notLoggedIn():
    return render_template("login.html", error="You must be logged in to do that.")

@dashboard.route('/dashboard')
def dashboardEndpoint():
    res = checkLogin()
    if res:
        return render_template("dashboard.html")
    else:
        return notLoggedIn()

@dashboard.route('/dashboard/you')
def dashboardYou():
    res = checkLogin()
    if res:
        return render_template("dashboard_you.html")
    else:
        return notLoggedIn()

@dashboard.route('/dashboard/leaderboard')
def dashboardLeaderboard():
    res = checkLogin()
    if res:
        return render_template("dashboard_leaderboard.html")
    else:
        return notLoggedIn()

@dashboard.route('/dashboard/profile')
def dashboardProfile():
    res = checkLogin()
    if res:
        return render_template("dashboard_profile.html")
    else:
        return notLoggedIn()

