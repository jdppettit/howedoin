import md5
from datetime import *

# INPUT: team id, user id, account id (all ints), item (string)
# OUTPUT: a hash that represents a token for rating auth

def makeToken(team_id, user_id, account_id, item, db):
    try:
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
    except Exception, e:
        error_log(e)
        return False

def makeIdentity(ip, db):
    try:
        user_hash = md5.new()
        user_hash.update(ip)
        user_hash.update(datetime.datetime.now())
        newIdentity = Rater(user_hash)
        db.session.add(newIdentity)
        db.session.commit()
        return user_hash.hexdigest()
    except Exception, e:
        error_log(e)
        return False


    
