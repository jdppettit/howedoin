from flask import *
from models import db

billing = Blueprint('billing', __name__, template_folder='templates')

@billing.route('/checkout', methods=['POST'])
def checkout():
    if request.method == "POST":
        if request.form['plan']
    else:
        abort(404)
