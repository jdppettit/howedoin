from flask import *
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.mail import *

from credentials import *
from password import *

from functions import *

import logging
from logging.handlers import RotatingFileHandler

ratings = Blueprint('ratings', __name__, template_folder='templates')

def nonTokenLogic(db, request, team_id, user_id, score, item_id=0):
    ip = request.remote_addr
    identity = makeIdentityHash(ip)
    check_id = checkIdentity(identity, db)
    if not check_id:
        # If the id is not something we've seen before
        identity = makeIdentity(identity, db)
        check_cookie = checkCookie(request, identity)
        if not check_cookie:
            # If the cookie is not present
            return render_template("rating.html", team_id=team_id, user_id=user_id, score=score, item_id=item_id,
            duplicate=0)
        elif check_cookie:
            # Cookie is present
            return render_template("rating.html", team_id=team_id, user_id=user_id, score=score, item_id=item_id,
            duplicate=1)
        else:
            abort(404)
    elif check_id:
        # If the id is something we've seen before
        check_cookie = checkCookie(request, identity)
        if not check_cookie:
            # Cookie not present
            return render_template("rating.html", team_id=team_id, user_id=user_id, score=score, item_id=item_id,
            duplicate=0)
        elif check_cookie:
            # Cookie present
            return render_template("rating.html", team_id=team_id, user_id=user_id, score=score, item_id=item_id,
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
    

@ratings.route('/rate/team/<team_id>/item/<item_id>/user/<user_id>/score/<score>', methods=['POST', 'GET'])
@ratings.route('/rate/team/<team_id>/item/<item_id>/user/<user_id>/score/<score>/token/<token>', methods=['POST', 'GET'])
@ratings.route('/rate/team/<team_id>/user/<user_id>/score/<score>', methods=['POST', 'GET'])
@ratings.route('/rate/team/<team_id>/user/<user_id>/score/<score>/token/<token>', methods=['POST', 'GET'])
def rate(team_id, user_id, score):
    try:
        if request.method == "GET":
            if team_id and item_id and user_id and score:
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
                else:
                    # Proceed with normal logic
                    nonTokenLogic(db, request, team_id, user_id, item_id)
            elif team_id and user_id and score:
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
                else:
                    nonTokenLogic(db, request, team_id, user_id, score)
            else:
                # If all of the required information was not provided error out
                return render_template("invalid.html", message=1)
        elif request.method == "POST":
            # Handle the form data
            if request.form['type'] == "token":
                tokenLogic()
            else:
                newRating = Rating()
                db.session.add(newRating)
                db.session.commit()
                return render_template("rating_complete.html")
        else:
            return abort(400)
    except Exception, e:
        app.logger.error(e)
        abort(404)
