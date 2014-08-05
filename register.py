from flask import *

register = Blueprint('register', __name__, template_folder='templates')

@register.route('/register', methods=['POST','GET'])
def registerEndpoint():
    try:
        if request.method == "GET":
            try:
                if session['logged_in']:
                    return render_template("dashboard.html", error="You are already registered and logged in.")
                else:
                    # if no logged_in var
                    return render_template("register.html")
            except:
                # if session vars not found (not logged in)
                return render_template("register.html")
        elif request.method == "POST":
            if request.form['username'] and request.form['name'] and request.form['email'] and request.form['password'] and request.form['passwordconfirm'] and request.form['plan']:
                if request.form['plan'] == 0:
                    # if plan is free, don't do billing, paidthru is forever
                    if request.form['company_name']:
                        # if company_name is there, use it   
                        print "test"
                    else:
                        print "test"
                        # if its not, provide empty string
                else:
                    # do billing, paidthru should be one month from now
                    if request.form['company_name']:
                        # if company name us it
                        print "test"
                    else:
                        print "test"
                        # if not use empty string
            else:
                return render_template("register.html", error="Please fill out all of the required fields.")
            # do all the registration stuff
            # if not on free plan, pass to billing
            # if on free plan, redirect to dashboard
    except:
        abort(404)
