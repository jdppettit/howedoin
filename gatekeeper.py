from flask import *
from models import *

'''
Action types:

1 - Add 
2 - Remove
3 - Modify
4 - Everything

Flow should be something like this:

1. Get user
2. Is the user an admin? Open the gate
3. Does the user have permission to do this? 
    a. Yes: open the gate
    b. No: gtfo

'''

def getPermissions(user_id, account_id, context, team_id=0)
    if team_id !=0:
        permissions = Permission.query.filter_by(user_id=user_id).filter_by(account_id=account_id).filter_by(team_id=team_id).filter_by(permission_type=context).all()
    else:
        permissions = Permission.query.filter_by(user_id=user_id).filter_by(account_id=account_id).filter_by(permission_type=context).all()
    return permissions

def checkPermissions(permissions, action, permission_type):
    action = int(action)
    for permission in permissions:
        if permission.permission_type = permission_type and permission.permission = action:
            return True
    return False

def checkSemiAdmin(user_id, account_id, context, team_id=0):
    if team_id != 0:
        permission = Permission.query.filter_by(user_id=user_id).filter_by(account_id=account_id).filter_by(permission_type=context).filter_by(team_id=team_id).filter_by(permission=5).first()
    else:
        permission = Permission.query.filter_by(user_id=user_id).filter_by(account_id=account_id).filter_by(permission_type=context).filter_by(permission=5).first()
    if permission:
        return True
    else:
        return False

def checkAdmin(user_id, account_id):
    check = Permission.query.filter_by(account_id=account_id).filter_by(user_id=user_id).filter_by(permission_type=99).first()
    if check:
        # yep, its an admin
        return True
    else:
        # nope, its a dirty user!
        return False

def teamGatekeeper(user_id, team_id, account_id, action):
    # check perms
    is_admin = checkAdmin(user_id, account_id)
    if is_admin:
        # its an admin, open gate
        return True
    else:
        # proceed
        context_admin = checkSemiAdmin(user_id, account_id, 1, team_id=team_id)
        if context_admin:
            # hes a semi admin, open gate
            return True
        else:
            # proceed
            permissions = getPermissions(user_id, account_id, 1, team_id=team_id)
            gatekeeper_status = checkPermissions(permissions, action, 1)
            if gatekeeper_status:
                # if permission found, open gate
                return True
            else:
                # nope, no dice, gate stays closed
                return False
    
def accountGatekeeper(user_id, account_id, action):
    # check perms
    is_admin = checkAdmin(user_id, account_id)
    if is_admin:
        # its an admin, open gate
        return True
    else:
        # proceed
        context_admin = checkSemiAdmin(user_id, account_id, 2)
        if context_admin:
            # hes a semi admin, open gate
            return True
        else:
            # proceed
            permissions = getPermissions(user_id, account_id, 2)
            gatekeeper_status = checkPermissions(permissions, action, 2)
            if gatekeeper_status:
                # if permission found, open gate
                return True
            else:
                # nope, no dice, gate stays closed
                return False



