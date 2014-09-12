from flask import *
from models import *

pages = Blueprint('pages', __name__, template_folder="templates")

@pages.route('/privacy')
def privacyPage():
    return render_template("privacy.html")

@pages.route('/terms')
def termsPage():
    return render_template("terms.html")

@pages.route('/api')
def apiPage():
    return render_template("api.html")

@pages.route('/demo')
def demoPage():
    return render_template("demo.html")
