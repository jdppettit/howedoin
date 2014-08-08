from flask import *
from flask import request
from models import db
from functions import doLogout

logout = Blueprint('logout', __name__, template_folder='templates')

@logout.route('/logout', methods=['GET'])
def logoutEndpoint():
    doLogout()
    return render_template("index.html", message="You have been logged out.")
