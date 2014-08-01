@app.route('/register', methods=['POST','GET'])
def register():
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
            # do all the registration stuff
            # if not on free plan, pass to billing
            # if on free plan, redirect to dashboard
    except:
        abort(404)
