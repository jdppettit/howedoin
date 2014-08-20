import md5
from datetime import *
from credentials import *
from flask import *
from models import *

# INPUT: team id, user id, account id (all ints), item (string)
# OUTPUT: a hash that represents a token for rating auth

def checkLogin():
    try:
        if session['username']:
            return True
    except:
        return False

def notLoggedIn():
    return render_template("login.html", error="You must be logged in to do that.")

def makeToken(team_id, user_id, account_id, item, db):
    token = md5.new()
    token.update(team_id)
    token.update(user_id)
    token.update(account_id)
    token.update(item)
    token.update(datetime.datetime.now())
    newToken = Token(account_id, user_id, token.hexdigest())
    db.session.add(newToken)
    db.session.commit()
    return True

def makeIdentity(user_hash, db):
    newIdentity = Rater(user_hash)
    db.session.add(newIdentity)
    db.session.commit()
    db.session.refresh(newIdentity)
    return True, newIdentity.id

def makeIdentityHash(ip):
    user_hash = md5.new()
    user_hash.update(ip)
    user_hash.update(USER_SALT)
    return user_hash.hexdigest()

def checkIdentity(user_hash, db):
    identity = Rater.query.filter_by(user_hash=user_hash).first()
    if identity:
        return True, identity.id
    else:
        return False, 0

def checkCookie(request, user_hash):
    print "User hash is: %s" % str(user_hash)
    check_string = 'howedoin_%s' % str(user_hash)
    if check_string in request.cookies:
        return True
    else:
        return False

def validateToken(token, db):
    checkedToken = Token.query.filter_by(token=token).first()
    if checkedToken:
        return True
    else:
        return False

def validateTeam(team_id):
    checkedTeam = Team.query.filter_by(id=team_id).first()
    if checkedTeam:
        return True
    else:
        return False

def validateUser(user_id):
    checkedUser = User.query.filter_by(id=user_id).first()
    if checkedUser:
        return True, checkedUser
    else:
        return False, 0

def validateUserMembership(user_id, team_id):
    checkMembership = Membership.query.filter_by(user_id=user_id).filter_by(team_id=team_id).first()
    if checkMembership:
        print checkMembership
        return True
    else:
        return False

def doLogout():
    session.pop('username', None)
    session.pop('name', None)
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('account_id', None)

def doLogin(user):
    session['username'] = user.username
    session['name'] = user.name
    session['user_id'] = user.id
    session['email'] = user.email
    session['account_id'] = user.account_id

def error_log(error, level):
    
    error_log = open('howedoin.log', 'w+')
    date = datetime.datetime.now()
    error_string = "[%s] [%s] - %s" % (str(date), level, error)
    error_log.write(error_string)
    error_log.close()
