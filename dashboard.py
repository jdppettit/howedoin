from flask import *
from functions import *
from models import *
from werkzeug import secure_filename

import os

dashboard = Blueprint('dashboard', __name__, template_folder='templates')

ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg'])
UPLOAD_FOLDER = "/srv/howedoin/static/uploads/user"

def allowed_file(filename):
    if filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS:
        return True, filename.rsplit('.',1)[1]

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

@dashboard.route('/dashboard/profile', methods=['GET','POST'])
def dashboardProfile():
    res = checkLogin()
    if res:
        if request.method == "GET":
            user = User.query.filter_by(id=session['user_id']).filter_by(account_id=session['account_id']).first()
            return render_template("dashboard_profile.html", user=user)
        elif request.method == "POST":
            user = User.query.filter_by(id=session['user_id']).filter_by(account_id=session['account_id']).first()
            if request.form.has_key('username'):
                user.username = request.form['username']
            if request.form.has_key('email'):
                user.email = request.form['email']
            if request.form.has_key('name'):
                user.name = request.form['name']
            if request.files['avatar']:
                avatar = request.files['avatar']
                resp, ext = allowed_file(avatar.filename)
                if avatar and resp:
                    avatar_filename = secure_filename("%s%s.%s" % (str(session['account_id']), str(session['user_id']),str(ext)))
                    avatar.save(os.path.join(UPLOAD_FOLDER, avatar_filename))
                    user.avatar = avatar_filename
            db.session.commit()
            return redirect('/dashboard/profile')
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
