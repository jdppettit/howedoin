from flask import *

dashboard = Blueprint('dashboard', __name__, template_folder='templates')

@dashboard.route('/dashboard')
def dashboardEndpoint():
    if session['username']:
        return render_template("dashboard.html")
    else:
        return render_template("login.html", error="You must be logged in to do that.")
