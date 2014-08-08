from flask import *
from models import db, User
from functions import *
from password import *

login = Blueprint('login', __name__, template_folder='templates')

@login.route('/login', methods=['POST','GET'])
def loginEndpoint():
    if request.method == "POST":
        if request.form['username'] and request.form['password']:
            print "got here"
            passwordHashed = hashPassword(request.form['password'])
            findUser = User.query.filter_by(username=request.form['username'], password=passwordHashed).first()
            if findUser:
                doLogin(findUser)
                print "did login"
                return redirect('/dashboard')
            else:
                # if no user found, invalid creds
                return render_template("login.html", error="Invalid credentials, please try again.")
        else:
            # if the user didn't provide username and password
            return render_template("login.html", error="Please enter a username and a password.")
    elif request.method == "GET":
        try:
            if session['username']:
                return render_template("dashboard.html")
        except KeyError:
            print "got to the except"
            # If the session variable doesn't exist (not logged in)
            return render_template("login.html")
