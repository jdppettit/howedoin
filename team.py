from models import db, Team, Account, User
from flask import *
from functions import *

team = Blueprint('team', __name__, template_folder='templates')

@team.route('/dashboard/team')
@team.route('/team')
def teamEndpoint():
    res = checkLogin()
    if res:
        teams = Team.query.filter_by(account_id=session['account_id']).all()
        return render_template("dashboard_team_view.html", teams=teams)
    else:
        return notLoggedIn()

def getAllUsers(account_id):
    users = User.query.filter_by(account_id=account_id).all()
    return users

def getMembers(team_id, account_id):
    return "poop"

def getTeamLeaderName(account_id, id):
    teamLeader = User.query.filter_by(account_id=account_id, id=id).first()
    return teamLeader.name

def addLeaderMembership(account_id, id, team_id):
    newMembership = Membership(account_id, id, team_id, is_admin=1)
    db.session.add(newMembership)
    db.session.commit()

def getTeamID(team):
    db.session.refresh(team)
    return team.id

@team.route('/dashboard/team/edit/<team_id>', methods=['POST','GET'])
@team.route('/team/edit/<team_id>', methods=['POST','GET'])
@team.route('/dashboard/team/<team_id>', methods=['POST','GET'])
@team.route('/team/<team_id>', methods=['POST','GET'])
def specificTeam(team_id):
    res = checkLogin()
    if res:
        if request.method == "GET":
            users = getAllUsers(session['account_id'])
            team = Team.query.filter_by(id=team_id).first()
            return render_template("dashboard_team_edit.html", team=team, users=users)
        elif request.method == "POST":
            # update the stuff
            team = Team.query.filter_by(id=team_id).first()
            team.team_name = request.form['name']
            team.team_leader_id = request.form['leader']
            team.team_leader_name = getTeamLeaderName(session['account_id'], request.form['leader'])
            db.session.commit()
            return redirect('/dashboard/team')
    else:
        return notLoggedIn()

@team.route('/dashboard/team/create', methods=['POST','GET'])
@team.route('/team/create', methods=['POST','GET'])
def teamCreate():
    res = checkLogin()
    if res:
        if request.method == "GET":
            users = getAllUsers(session['account_id'])
            return render_template("dashboard_team_create.html", users=users)
        elif request.method == "POST":
            if request.form['name'] and request.form['leader']:
                team_leader_name = getTeamLeaderName(session['account_id'], request.form['leader'])
                newTeam = Team(session['account_id'], request.form['name'], team_leader_name, request.form['leader'])
                db.session.add(newTeam)
                db.session.commit()
                addLeaderMembership(session['account_id'], request.form['leader'], getTeamID(newTeam))
                return redirect('/dashboard/team')
            else:
                return render_template('/dashboard/team/create', users=getAllUsers(session['account_id']), error="A team name is required.")
    else:
        return notLoggedIn()

@team.route('/dashboard/team/delete/<team_id>')
@team.route('/team/delete/<team_id>')
def teamDelete(team_id):
    return render_template("dashboard_team_delete.html")

@team.route('/dashboard/team/user/add/<user_id>')
@team.route('/team/user/add/<user_id>')
def teamAddUser(user_id):
    return render_template("dashboard_team_user_add.html")

@team.route('/dashboard/team/user/delete/<user_id>')
@team.route('/team/user/delete/<user_id>')
def teamDeleteUser(user_id):
    return render_template("dashboard_team_user_delete.html")

@team.route('/dashboard/team/user/edit/<user_id>')
@team.route('/team/user/edit/<user_id>')
def teamUserEdit(team_id):
    return render_template("dashboard_team_user_edit.html")
