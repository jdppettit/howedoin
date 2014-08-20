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

def checkScoreMakeRating(account_id, user_id, team_id, score, username, rater_email="", rater_name="", rater_id="",
comment="", duplicate=0):
    if score != 0:
        newRating = Rating(account_id, user_id, team_id, score, username, rater_email=rater_email, rater_name=rater_name, rater_id=rater_id, comment=comment, duplicate=duplicate)
        db.session.add(newRating)
        db.session.commit()

def nonTokenLogic(db, request, team_id, user_id, account_id, score=0, item_id=0):
    ip = request.remote_addr
    identity = makeIdentityHash(ip)
    check_id, rater_id = checkIdentity(identity, db)
    if not check_id:
        # If the id is not something we've seen before
        identity, rater_id = makeIdentity(identity, db)
        check_cookie = checkCookie(request, identity)
        if check_cookie == False:
            # If the cookie is not present
            # need to make the cookie
            resp = make_response(render_template("rating.html", rater_id=rater_id, team_id=team_id, user_id=user_id, score=score, item_id=item_id,
            duplicate=0))
            resp.set_cookie("howedoin_%s" % identity)
            return resp
        elif check_cookie == True:
            # Cookie is present
            return render_template("rating.html", rater_id=rater_id, team_id=team_id, user_id=user_id, score=score, item_id=item_id,
            duplicate=1)
        else:
            abort(404)
    elif check_id:
        # If the id is something we've seen before
        check_cookie = checkCookie(request, identity)
        if check_cookie == False:
            # Cookie not present
            # need to make the cookie
            resp = make_response(render_template("rating.html", rater_id=rater_id, team_id=team_id, user_id=user_id, score=score, item_id=item_id,
            duplicate=0))
            resp.set_cookie("howedoin_%s" % identity)
            return resp
        elif check_cookie == True:
            # Cookie present
            return render_template("rating.html", rater_id=rater_id, team_id=team_id, user_id=user_id, score=score, item_id=item_id,
            duplicate=1)
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
    
@ratings.route('/rate/team/<team_id>/user/<user_id>', methods=['POST', 'GET'])
def rateNoScoreNoItem(team_id, user_id):
    userValidate, user = validateUser(user_id)
    teamValdiate = validateTeam(team_id)
    userMembershipValidate = validateTeam(team_id)
    if request.method == "GET":
        return nonTokenLogic(db, request, team_id, user_id, user.account_id)
    elif request.method == "POST":
        rater_email = ""
        rater_name = ""
        rater_id = request.form['rater_id']
        score = int(request.form['score'])
        comment = ""
        if request.args.has_key('comment'):
            comment = request.form['comment']
        if 'email' in request.args:
            rater_email = request.form['email']
        if 'name' in request.args:
            rater_name = request.form['name']

        user = User.query.filter_by(id=user_id).first()
        newRating = Rating(user.account_id, user.id, team_id, score, user.username, rater_email=rater_email,
        rater_name=rater_name, rater_id=rater_id, comment=comment, duplicate=request.form['duplicate'])
        db.session.add(newRating)
        db.session.commit()
        return render_template("rating_complete.html")


@ratings.route('/rate/team/<team_id>/item/<item_id>/user/<user_id>/score/<score>', methods=['POST', 'GET'])
@ratings.route('/rate/team/<team_id>/user/<user_id>/score/<score>', methods=['POST', 'GET'])
def rate(team_id, user_id, score):
    userValidate, user = validateUser(user_id)
    teamValidate = validateTeam(team_id)
    userMembershipValidate = validateUserMembership(user_id, team_id)
    if request.method == "GET":
        try:
            if team_id and item_id and user_id and score and userValidate and teamValidate and userMembershipValidate:
                try:
                    if token:
                        # Check token validity
                        tokenStatus = validateToken(token, db)
                        if tokenStatus:
                            # Token is valid
                            # Make the rating
                            return render_template("rating.html", token=token, team_id=team_id, item_id=item_id,
                            user_id=user_id, score=score)
                        else:
                            # Token invalid
                            # Tell them it is invalid
                            return render_template("invalid.html", message=0)
                except:
                    # Proceed with normal logic
                    return nonTokenLogic(db, request, team_id, user_id, user.account_id, score=score, item_id=item_id)
        except:
            if team_id and user_id and score and userValidate and teamValidate and userMembershipValidate:
                try:
                    if token:
                        tokenStatus = validateToken(token, db)
                        # Check token validity
                        if tokenStatus:
                            # Token is valid
                            # make the rating
                            return render_template("rating.html", token=token, team_id=team_id,
                            user_id=user_id, score=score)
                        else:
                            # Token is invalid
                            # Tell them it is invalid
                            return render_template("invalid.html", message=0)
                except:
                    # If there is no token
                    return nonTokenLogic(db, request, team_id, user_id, user.account_id, score)
            else:
                # If all of the required information was not provided error out
                return render_template("invalid.html", message=1)
    elif request.method == "POST":
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
        rater_name=rater_name, rater_id=rater_id, comment=comment, duplicate=int(request.form['duplicate']))
        db.session.add(newRating)
        db.session.commit()
        return render_template("rating_complete.html")

@ratings.route('/rate/team/<team_id>/user/<user_id>/score/<score>/token/<token>', methods=['POST', 'GET'])
@ratings.route('/rate/team/<team_id>/item/<item_id>/user/<user_id>/score/<score>/token/<token>', methods=['POST','GET'])
def rateToken(team_id, user_id, score, token):
    return "This isn't made yet"    
