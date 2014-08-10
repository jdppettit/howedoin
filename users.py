from models import db
from flask import *

users = Blueprint('users', __name__, template_folder='templates')

@users.route('/dashboard/user/add')
@users.route('/user/add')
def userAdd():
    # adds a user

@users.route('/dashboard/user/edit/<user_id>')
@users.route('/user/edit/<user_id')
def userEdit(user_id):
    # edits a user

@users.route('/dashboard/user/delete/<user_id>')
@users.route('/user/delete/<user_id>')
def userDelete(user_id):
    # deletes a user

@users.route('/user/activate/<token>')
def userActivate(token):
    # activates a new user account

