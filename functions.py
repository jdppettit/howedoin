import md5
from datetime import *

# INPUT: team id, user id, account id (all ints), item (string)
# OUTPUT: a hash that represents a token for rating auth

def makeToken(team_id, user_id, account_id, item):
    token = md5.new()
    token.update(team_id)
    token.update(user_id)
    token.update(account_id)
    token.update(item)
    token.update(datetime.datetime.now())
    return token


