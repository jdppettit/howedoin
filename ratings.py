from flask import *
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.mail import *
from models import db, Membership, User, Team, Rating, Rater
from credentials import *
from password import *

from functions import *

from pprint import *
import logging
from logging.handlers import RotatingFileHandler

ratings = Blueprint('ratings', __name__, template_folder='templates')

def checkScoreMakeRating(account_id, user_id, team_id, score, rater_email="", rater_name="", rater_id="",
comment="", duplicate=0):
    if score != 0:
        user = User.query.filter_by(id=user_id).first()
        newRating = Rating(account_id, user_id, team_id, score, user.username, rater_email=rater_email, rater_name=rater_name, rater_id=rater_id, comment=comment, duplicate=duplicate)
        db.session.add(newRating)
        db.session.commit()
        db.session.refresh(newRating)
        return newRating.id

def nonTokenLogic(db, request, team_id, user_id, account_id, postURL, score=0, item_id=0):
    ip = request.remote_addr
    identity = makeIdentityHash(ip)
    check_id, rater_id = checkIdentity(identity, db)
    rating_id = 0
    score = int(score)
    if not check_id:
        # If the id is not something we've seen before
        identity, rater_id = makeIdentity(identity, db)
        check_cookie = checkCookie(request, identity)
        if check_cookie == False:
            # If the cookie is not present
            # need to make the cookie
            if score != 0:
                    rating_id = checkScoreMakeRating(account_id, user_id, team_id, score, duplicate=0)
            resp = make_response(render_template("rating.html", rater_id=rater_id, team_id=team_id, user_id=user_id, score=score, item_id=item_id,
            duplicate=0, postURL=postURL, rating_id=rating_id))
            resp.set_cookie("howedoin_%s" % identity)
            return resp
        elif check_cookie == True:
            # Cookie is present
            if score != 0:
                    rating_id = checkScoreMakeRating(account_id, user_id, team_id, score, duplicate=1)
            return render_template("rating.html", rater_id=rater_id, team_id=team_id, user_id=user_id, score=score, item_id=item_id,
            duplicate=1, postURL=postURL, rating_id=rating_id)
        else:
            abort(404)
    elif check_id:
        # If the id is something we've seen before
        check_cookie = checkCookie(request, identity)
        if check_cookie == False:
            # Cookie not present
            # need to make the cookie
            if score != 0:
                    rating_id = checkScoreMakeRating(account_id, user_id, team_id, score, duplicate=0)
            resp = make_response(render_template("rating.html", rater_id=rater_id, team_id=team_id, user_id=user_id, score=score, item_id=item_id,
            duplicate=0, postURL=postURL, rating_id=rating_id))
            resp.set_cookie("howedoin_%s" % identity)
            return resp
        elif check_cookie == True:
            # Cookie present
            if score != 0:
                    rating_id = checkScoreMakeRating(account_id, user_id, team_id, score, duplicate=1)
            return render_template("rating.html", rater_id=rater_id, team_id=team_id, user_id=user_id, score=score, item_id=item_id,
            duplicate=1, postURL=postURL, rating_id=rating_id)
        else:
            abort(404)
    else:
        abort(404)

def tokenLogic(db, request, token, team_id, user_id, score, item_id=0):
    # invalidate token
    oldToken = Token.query.filter_by(token=token).first()
    db.session.remove(oldToken)
    # make the new rating
    newRating = Rating()
    db.session.commit()
    return render_template("rating_complete.html")

def handlePost(request, user_id=0, team_id=0, item_id=0):
    if request.form['rating_id'] != "0":
        # update old rating
        oldRating = Rating.query.filter_by(id=request.form['rating_id']).first()
        rater_email = ""
        rater_name = ""
        rater_id = request.form['rater_id']
        score = int(request.form['score'])
        comment = ""
        if request.form.has_key('comment'):
            comment = request.form['comment']
        if request.form.has_key('email'):
            rater_email = request.form['email']
        if request.form.has_key('name'):
            rater_name = request.form['name']

        user = User.query.filter_by(id=user_id).first()
        oldRating.comment = comment
        oldRating.rater_email = rater_email
        oldRating.rater_name = rater_name
        oldRating.score = score 
        oldRating.rater_id = rater_id
        db.session.commit()
        return render_template("rating_complete.html")
    else:
        # make new rating
        rater_email = ""
        rater_name = ""
        rater_id = request.form['rater_id']
        score = int(request.form['score'])
        comment = ""
        if request.form.has_key('comment'):
            comment = request.form['comment']
        if request.form.has_key('email'):
            rater_email = request.form['email']
        if request.form.has_key('name'):
            rater_name = request.form['name']

        user = User.query.filter_by(id=user_id).first()
        newRating = Rating(user.account_id, user.id, team_id, score, user.username, rater_email=rater_email,
        rater_name=rater_name, rater_id=rater_id, comment=comment, duplicate=request.form['duplicate'])
        db.session.add(newRating)
        db.session.commit()
        return render_template("rating_complete.html")


@ratings.route('/rate/team/<team_id>/user/<user_id>/score/<score>', methods=['POST','GET'])
def rateScoreNoItem(team_id, user_id, score):
    userValidate, user = validateUser(user_id)
    teamValidate = validateTeam(team_id)
    userMembershipValidate = validateTeam(team_id)
    postURL = "/rate/team/%s/user/%s/score/%s" % (str(team_id), str(user_id), str(score))
    if userValidate and teamValidate and userMembershipValidate and team_id and user_id and score:
        if request.method == "GET":
            return nonTokenLogic(db, request, team_id, user_id, user.account_id, postURL, score=score)
        elif request.method == "POST":
            return handlePost(request, team_id=team_id, user_id=user_id)
    else:
        return render_template("rating_error.html")
 
@ratings.route('/rate/team/<team_id>/user/<user_id>', methods=['POST', 'GET'])
def rateNoScoreNoItem(team_id, user_id):
    userValidate, user = validateUser(user_id)
    teamValidate = validateTeam(team_id)
    userMembershipValidate = validateTeam(team_id)
    postURL = "/rate/team/%s/user/%s" % (str(team_id), str(user_id))
    if userValidate and teamValidate and userMembershipValidate and team_id and user_id:
        if request.method == "GET":
            return nonTokenLogic(db, request, team_id, user_id, user.account_id, postURL)
        elif request.method == "POST":
            return handlePost(request, team_id=team_id, user_id=user_id)
    else:
        return render_template("rating_error.html")

@ratings.route('/rate/team/<team_id>/item/<item_id>/user/<user_id>/score/<score>', methods=['POST','GET'])
def rateItemScore(team_id, item_id, user_id, score):
    userValidate, user = validateUser(user_id)
    teamValidate = validateTeam(team_id)
    userMembershipValidate = validateTeam(team_id)
    postURL = "/rate/team/%s/item/%s/user/%s/score/%s" % (str(team_id), str(item_id), str(user_id), str(score))
    if userValidate and teamValidate and userMembershipValidate and team_id and item_id and user_id and score:
        if request.method == "GET":
            return nonTokenLogic(db, request, team_id, user_id, user.account_id, postURL, item_id=item_id, score=score)
        elif request.method == "POST":
            return handlePost(request, team_id=team_id, item_id=item_id, user_id=user_id)
    else:
        return render_template("rating_error.html") 

@ratings.route('/rate/team/<team_id>/item/<item_id>/user/<user_id>', methods=['POST','GET'])
def rateNoScoreItem(team_id, item_id, user_id):
    userValidate, user = validateUser(user_id)
    teamValidate = validateTeam(team_id)
    userMembershipValidate = validateTeam(team_id)
    postURL = "/rate/team/%s/item/%s/user/%s" % (str(team_id), str(item_id), str(user_id))
    if userValidate and teamValidate and userMembershipValidate and team_id and item_id and user_id:
        if request.method == "GET":
            return nonTokenLogic(db, request, team_id, user_id, user.account_id, postURL, item_id=item_id)
        elif request.method == "POST":
            return handlePost(request, team_id=team_id, item_id=item_id, user_id=user_id)
    else:
        return render_template("rating_error.html")

