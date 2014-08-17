from flask import *
from functions import *
from models import *

dashboard = Blueprint('dashboard', __name__, template_folder='templates')

def getAllRatings(account_id):
    ratings = Rating.query.filter_by(account_id=account_id).all()
    return ratings

@dashboard.route('/dashboard/rating/link')
def dashboardRatingLink():
    res = checkLogin()
    if res:
        teams = Team.query.filter_by(account_id=session['account_id']).all()
        user = User.query.filter_by(id=session['user_id']).first()
        return render_template("dashboard_rating_link.html", teams=teams, user=user)
    else:
        return notLoggedIn()

@dashboard.route('/dashboard/you')
@dashboard.route('/dashboard/rating/you')
def dashboardRatingYou():
    res = checkLogin()
    if res:
        ratings = Rating.query.filter_by(user_id=session['user_id'], account_id=session['account_id']).all()
        return render_template("dashboard_rating_you.html", ratings=ratings)
    else:
        return notLoggedIn()

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

@dashboard.route('/dashboard/rating/all')
def dashboardRatingsAll():
    res = checkLogin()
    if res:
        allRatings = getAllRatings(session['account_id'])
        return render_template("dashboard_rating_view_all.html", ratings=allRatings)
    else:
        return notLoggedIn()
