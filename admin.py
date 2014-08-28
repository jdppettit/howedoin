from flask import *
from password import *
from models import *

admin = Blueprint('admin', __name__, template_folder="templates")

def checkAdminLogin():
    try:
        if session['is_admin'] == 1 and session['username']:
            return True
    except:
        return False

def adminNotLoggedIn():
    return redirect('/admin/login')

def doAdminLogin(username, password):
    # If logged in as a normal user log out
    session.pop('username', None)
    session.pop('name', None)
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('account_id', None)

    hashedPassword = hashPassword(password)
    admin = Administrator.query.filter_by(username=username).filter_by(password=hashedPassword).first()
    if admin:
        session['username'] = admin.username
        session['name'] = admin.name
        session['admin_id'] = admin.id
        session['email'] = admin.email
        session['is_admin'] = 1
        return redirect('/admin')
    else:
        return redirect('/')

def doAdminLogout():
        session.pop('username', None)
        session.pop('name', None)
        session.pop('admin_id', None)
        session.pop('email', None)
        session.pop('is_admin', None)
        return redirect('/admin/login')

@admin.route('/admin/login', methods=['POST','GET'])
def adminLogin():
    if request.method == "GET":
        return render_template("admin_login.html")
    elif request.method == "POST":
        if request.form.has_key('username') and request.form.has_key('password'):
            return doAdminLogin(request.form['username'], request.form['password'])
        else:
            return redirect('/')

@admin.route('/admin/logout')
def adminLogout():
    res = checkAdminLogin()
    if res:
        return doAdminLogout()
    else:
        return redirect('/admin/login')

@admin.route('/admin')
def adminDashboard():
    res = checkAdminLogin()
    if res:
        return render_template("admin_dashboard.html")
    else:
        return adminNotLoggedIn()

@admin.route('/admin/account/search', methods=['POST','GET'])
def adminAccountSearch():
    res = checkAdminLogin()
    if res:
        if request.method == "GET":
            return render_template("admin_account_search.html")
        elif request.method == "POST":
            account = Account.query.filter_by(id=request.form['search']).first()
            users = User.query.filter_by(account_id=account.id).all()
            return render_template("admin_account_view.html", account=account, users=users)
    else:
        return adminNotLoggedIn()
