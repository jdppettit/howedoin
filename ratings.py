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

@ratings.route('/rate/team/<team_id>/user/<user_id>/score/<score>')
def rate(team_id, user_id, score):
    try:
        ip = request.remote_addr
        identity = makeIdentityHash(ip)
        check_id = checkIdentity(identity, db)
        if not check_id:
            # If the identity is not already in the db
            identity = makeIdentity(ip, db)
            check_cookie = checkCookie(request, identity)
            if not check_cookie:
                # If the cookie is not present
                print "foo"
            elif check_cookie:
                # If the cookie is present
                print "foo"
            else:
                abort(500)

        elif check_id:
            # If the identity is in the database
            check_cookie = checkCookie(request, identity)
            if not check_cookie:
                # If the cookie is not present
                print "foo"
            elif check_cookie:
                # If the cookie is present
                print "foo"
            else:
                abort(500)
        else:
            # If it returns 0 or anything else weird 
            abort(500)

    except Exception, e:
        app.logger.error(e)
        abort(404)
