from flask import *

login = Blueprint('login', __name__, template_folder='templates')

@login.route('/login', methods=['POST','GET'])
def loginEndpoint():
    try:
        if request.method == "POST":
            if request.form['username'] and request.form['password']:
                passwordHashed = hashPassword(request.form['password'])
                findUser = User.query.filter_by(username=username, password=passwordHased).first()
                if findUser:
                    # set session vars
                    # login
                    # redirect to dashboard
                    return redirect('/dashboard')
                else:
                    # if no user found, invalid creds
                    return render_template("login.html", error="Invalid credentials, please try again.")
            else:
                # if the user didn't provide username and password
                return render_template("login.html", error="Please enter a username and a password.")
        elif request.method == "GET":
            try:
                if session['logged_in']:
                    return render_template("dashboard.html")
                else:
                    return render_template("login.html")
            except:
                # If the session variable doesn't exist (not logged in)
                return render_template("login.html")
    except:
        abort(404)
