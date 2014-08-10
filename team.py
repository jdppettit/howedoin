from models import db
from flask import *

team = Blueprint('team', __name__, template_folder='templates')

@team.route('/dashboard/team')
@team.route('/team')
def teamEndpoint():
    # get all teams for this account
    # print them

@team.route('/dashboard/team/<team_id>')
@team.route('/team/<team_id>')
def specificTeam(team_id):
    # list stuff about one team

@team.route('/dashboard/team/create')
@team.route('/team/create')
def teamCreate():
    # make a team

@team.route('/dashboard/team/delete/<team_id>')
@team.route('/team/delete/<team_id>')
def teamDelete(team_id):
    # delete a team

@team.route('/dashboard/team/user/add/<user_id>')
@team.route('/team/user/add/<user_id>')
def teamAddUser(user_id):
    # add a user to a team

@team.route('/dashboard/team/user/delete/<user_id>')
@team.route('/team/user/delete/<user_id>')
def teamDeleteUser(user_id):
    # delete a user from a team

@team.route('/dashboard/team/edit/<team_id>')
@team.route('/team/edit/<team_id>')
def teamEdit(team_id):
    # edit a team

@team.route('/dashboard/team/user/edit/<user_id>')
@team.route('/team/user/edit/<user_id>')
def teamUserEdit(team_id):
    # edits a team user
