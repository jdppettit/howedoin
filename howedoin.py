from flask import *
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.mail import *

from credentials import *
from password import *

import random
import string

app = Flask(__name__)
connectionString = "mysql://%s:%s@%s:3306/%s" % (USERNAME, PASSWORD, HOSTNAME, DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = connectionString
db = SQLAlchemy(app)
app.secret_key = SECRET_KEY

app.config.update(
		MAIL_SERVER=EMAIL_SERVER,
		MAIL_PORT=587,
		MAIL_USE_TLS=True,
		MAIL_USERNAME=EMAIL_USERNAME,
		MAIL_PASSWORD=EMAIL_PASSWORD
	)

mail = Mail(app)

class Account(db.Model):
	__tablename__ = "account"
	
	id = db.Column(db.Integer, primary_key=True)
	company_name = db.Column(db.String(25))
	address1 = db.Column(db.String(30))
	address2 = db.Column(db.String(30))
	state = db.Column(db.String(15))
	zip = db.Column(db.Integer)
	plan_id = db.Column(db.Integer)
	paid_thru = db.Column(db.String(20))
	is_current = db.Column(db.Integer)
	stripe_customer = db.Column(db.String(20))

	def __init__(self, id, company_name, plan_id, paid_thru, is_current):
		self.id = id
		self.company_name = company_name
		self.plan_id = plan_id
		self.paid_thru = paid_thru
		self.is_current = is_current

class Team(db.Model):
	__tablename__ = "team"

	id = db.Column(db.Integer, primary_key=True)
	account_id = db.Column(db.Integer)
	team_name = db.Column(db.String(50))
	team_leader = db.Column(db.Integer)
	team_avatar = db.Column(db.String(100))

	def __init__(self, account_id, team_name, team_leader):
		self.account_id = account_id
		self.team_name = team_name
		self.team_leader = team_leader

class User(db.Model):
	__tablename__ = "user"

	id = db.Column(db.Integer, primary_key=True)
	account_id = db.Column(db.Integer)
	name = db.Column(db.String(35))
	username = db.Column(db.String(35))
	password = db.Column(db.String(50))
	email = db.Column(db.String(40))
	teams = db.Column(db.String(50))
	active = db.Column(db.Integer)
	activation_link = db.Column(db.String(10))
		
	def __init__(self, account_id, name, username, password, email, teams, active=1, activation_link=""):
		self.account_id = account_id
		self.name = name
		self.username = username
		self.password = password
		self.email = email
		self.teams = teams
		self.active = active
		self.activation_link = activation_link

class Rating(db.Model):
	__tablename__ = "rating"

	id = db.Column(db.Integer, primary_key=True)
	account_id = db.Column(db.Integer)
	user_id = db.Column(db.Integer)
	team_id = db.Column(db.Integer)
	item_number = db.Column(db.String(25))
	score = db.Column(db.Integer)
	comment = db.Column(db.Text)
	username = db.Column(db.String(35))

	def __init__(self, account_id, user_id, item_number, score, username):
		self.account_id = account_id
		self.user_id = user_id
		self.item_number = item_number
		self.score = score
		self.username = username

class Membership(db.Model):
	__tablename__ = "membership"
	
	id = db.Column(db.Integer, primary_key=True)
	account_id= db.Column(db.Integer)
	user_id = db.Column(db.Integer)
	team_id = db.Column(db.Integer)
	is_admin = db.Column(db.Integer)
	
	def __init__(self, account_id, user_id, team_id, is_admin):
		self.account_id = account_id
		self.user_id = user_id
		self.team_id = team_id
		self.is_admin = is_admin
	
db.create_all()
db.session.commit()

def getActivationURL(size=6, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

@app.route('/')
def index():
	try:
		if session['username']:
			return redirect('/dashboard')
		else:
			return render_template('index.html')
	except Exception, e:
		return render_template('index.html')

@app.route('/rate/<team_id>/item/<item_id>/user/<username>/<score>')
def makeRating(team_id, item_id, username, score):
	try:
		if team_id and item_id and username and score:
			team = Team.query.filter_by(id=team_id).first()
			if team:
				user = User.query.filter_by(username=username, account_id=team.account_id).first()
				if user:
					if int(score) >= 1 and int(score) <= 3:
						if request.cookies.get('rated_user_%s' % str(user.id)):
							cookie = request.cookies.get('rated_user')
							print cookie
							checkString = "%s-%s" % (str(user.id), str(item_id))
							if checkString == cookie:
								oldRating = Rating.query.filter_by(user_id=user.id, item_number=item_id).first()
								oldRating.score = score
								db.session.commit()
								# do update logic
								rating = Rating.query.filter_by(account_id=team.account_id, user_id=user.id, item_number=item_id).first()
								rating_id = rating.id
								return render_template("add_rating.html", team_id=team_id, item_id=item_id, username=username,score=score,rating_id=rating_id)
							else:
								return "poop"							

						else:
							rating = Rating(team.account_id, user.id, item_id, int(score), username)
							db.session.add(rating)
							db.session.commit()
							rating = Rating.query.filter_by(account_id=team.account_id, user_id=user.id, item_number=item_id).first()
							rating_id = rating.id
							resp = make_response(render_template("add_rating.html", team_id=team_id, item_id=item_id, username=username, score=score, rating_id=rating_id))
							resp.set_cookie('rated_user_%s' % str(user.id),"%s-%s" % (str(user.id), str(item_id)))
							return resp
					else:
						return render_template("index.html", error="Please enter a score between 1 and 3")
				else:
					return render_template('index.html', error="That user doesn't exist!")
			else:
				return render_template('index.html', error="That team doesn't exist!")	
	except Exception, e:
		print e
		return render_template('index.html', error="That team or username does not exist.")

@app.route('/rate/<team_id>/item/<item_id>/user/<username>/<score>/update/<rating_id>', methods=['POST'])
def updateRating(team_id, item_id, username, score, rating_id):
	try:
		if team_id and item_id and username and score and rating_id:
			rating = Rating.query.filter_by(id=rating_id).first()
			if rating:
				if request.form['comment']:
					rating.comment = request.form['comment']
					db.session.commit()
					return render_template('index.html', message="Rating successfully added.")
				else:
					return render_template('index.html', message="Rating successfully added.")
			else:
				return render_template('index.html', error="Invalid rating ID")
		else:
			return render_template('index.html', error="Missing information!")
	except Exception, e:
		print e
                return render_template('index.html', error="That team or username does not exist.")


@app.route('/dashboard')
def dashboard():
	if session['username']:
		teams = Team.query.filter_by(account_id=session['account_id']).all()
		account = Account.query.filter_by(id=session['account_id']).all()
		users = User.query.filter_by(account_id=session['account_id']).all()
		ratings = Rating.query.filter_by(account_id=session['account_id']).all()
		numRatings = len(ratings)
		numBad = 0.00
		numMed = 0.00
		numGod = 0.00
		for rating in ratings:
			if rating.score == 1:
				numBad += 1
				print "One bad"
			elif rating.score == 2:
				numMed += 1
				print "One med"
			elif rating.score == 3:
				numGod += 1
				print "One good"
		if numBad != 0:
			percentBad = (numBad / numRatings) * 100.00
		else:
			percentBad = 0
	
		if numMed != 0:
			percentMed = (numMed / numRatings) * 100.00
		else:
			percentMed = 0
	
		if numGod != 0:
			percentGod = (numGod / numRatings) * 100.00
		else:
			percentGod = 0
		
		percentBad = round(percentBad, 2)
		percentGod = round(percentGod, 2)
		percentMed = round(percentMed, 2)

		return render_template('dashboard.html', teams=teams, account=account, users=users, ratings=ratings, num_ratings=numRatings, percentBad = percentBad, percentMed = percentMed, percentGod = percentGod)
	else:
		return render_template('login.html', error="You must be logged in first.")

@app.route('/dashboard/link')
def link():
	return render_template("link.html", team_id=3, username=session['username'])

@app.route('/dashboard/rating')
def dashboardRatings():
	ratings = Rating.query.filter_by(account_id=session['account_id']).all()
	return render_template("dashboard_ratings.html", ratings=ratings)

@app.route('/dashboard/team')
def dashboardTeams():
	return render_template("dashboard_teams.html")

@app.route('/dashboard/users')
def dashboardUsers():
	users = User.query.filter_by(account_id=session['account_id']).all()
	return render_template("dashboard_users.html", users=users)

@app.route('/team/add', methods=['POST','GET'])
def teamAdd():
	if request.method == "POST":
		if request.form['team_name'] and request.form['team_leader']:
			team = Team(session['account_id'], request.form['team_name'], request.form['team_leader'])
			db.session.add(team)
			db.session.commit()
			return redirect('/dashboard')
		else:
			users = User.query.filter_by(account_id=session['account_id']).all()
			return render_template('add_team.html', users=users, error="Please enter a team name and select a team leader.")
		return "Add a team"
	elif request.method == "GET":
		users = User.query.filter_by(account_id=session['account_id']).all()
		return render_template('add_team.html', users=users)

@app.route('/user/add', methods=['POST','GET'])
def userAdd():
	if request.method == "POST":
		if request.form['username'] and request.form['email'] and request.form['name']:
			subject = "%s wants to add you to Howedoin!" % session['name']
			activation_url = getActivationURL(10)
			msg = Message(subject, sender="Howedoin <donotreply@howedo.in>",recipients=[request.form['email']])
			msg.html = "Hello %s!<br/><br/>%s would like you add you to their Howedoin account! Howedoin lets you measure your customer satisfaction and receive useful feedback (and maybe rewards)! To finish up the process, you'll just need to make a password and sign in. Please click the link below to complete your sign up:<br/><br/><a href=\"https://howedo.in/user/activate/%s\">https://howedo.in/user/activate/%s</a><br/><br/>Thanks for signing up!<br/><br/>Regards,<br/><br/>The Howedoin Team<br/><a href=\"https://howedo.in\">https://howedo.in</a>" % (request.form['name'], session['name'], activation_url, activation_url)
			teams = Team.query.filter_by(account_id=session['account_id'])
			user = User(session['account_id'], request.form['name'], request.form['username'], hashPassword(getActivationURL(25)), request.form['email'], "", 0, activation_url)
			db.session.add(user)
			db.session.flush()
			db.session.refresh(user)
			for team in teams:
                        	if str(team.id) in request.form:
                                        newMembership = Membership(session['account_id'], user.id, team.id, 0)
                                        db.session.add(newMembership)
			db.session.commit()
			mail.send(msg)
			return redirect('/dashboard')
		else:
			return render_template('add_user.html', error="Please fill out all of the fields and try again")
	elif request.method == "GET":
		teams = Team.query.filter_by(account_id=session['account_id'])
		return render_template('add_user.html', teams=teams)

@app.route('/team/edit/<team_id>', methods=['GET','POST'])
def teamEdit(team_id):
	if request.method == "POST":
		if team_id:
			return "Poop"
		else:
			return render_template("dashboard.html", error="That wasn't a valid team ID.")
	elif request.method == "GET":
		if team_id:
			team = Team.query.filter_by(id=team_id).first()
			users = User.query.filter_by(account_id=session['account_id']).all()
			return render_template("edit_team.html", team=team, users=users)
		else:
			return render_template("dashboard.html", error="That wasn't a valid team ID.")

@app.route('/user/edit/<user_id>', methods=['GET','POST'])
def userEdit(user_id):
	if request.method == "POST":
		if user_id:
			return "poop"		
		else:
			return render_template("dashboard.html", error="That wasn't a valid user ID.")
	elif request.method == "GET":
		if user_id:
			you = User.query.filter_by(id=user_id).first()
			teams = Team.query.filter_by(account_id=session['account_id']).all()
			membership = Membership.query.filter_by(account_id=session['account_id'], user_id=user_id).all()
			membership_list = []
			for member in membership:
				membership_list.append(member.team_id)
			return render_template("edit_user.html", user=you, teams=teams, membership=membership_list)
		else:
			return render_template("dashboard.html", error="That wasn't a valid user ID.")

@app.route('/user/activate/<activation_string>', methods=['GET','POST'])
def userActivate(activation_string):
	if request.method == "GET":
		if activation_string:
			you = User.query.filter_by(activation_link=activation_string).first()
			if you:
				return redirect("/user/activate/%s/form" % activation_string)
			else:
				return render_template("index.html", error="That is not a valid activation URL.")
		else:
			return render_template("index.html", error="That is not a valid activation URL.")

@app.route('/user/activate/<activation_string>/form', methods=['GET','POST'])
def userActivateForm(activation_string):
	if request.method == "GET":
		return render_template("user_activate.html", activation_string=activation_string)
	elif request.method == "POST":
		if activation_string:
                        if request.form['password'] and request.form['password_again'] and request.form['email']:
                                you = User.query.filter_by(activation_link=activation_string, email=request.form['email']).first()
                                if request.form['password'] == request.form['password_again']:
                                        if you:
                                                hashedPassword = hashPassword(request.form['password'])
                                                you.password = hashedPassword
                                                db.session.commit()

                                                session['username'] = you.username
                                                session['name'] = you.name
                                                session['user_id'] = you.id
                                                session['account_id'] = you.account_id
                                                session['teams'] = you.teams
                                                session['email'] = you.email

                                                return redirect('/dashboard')
                                        else:
                                                return render_template("index.html", error="Your email does not match an existing user.")
                                else:
                                        return render_template("index.html", error="Your passwords do not match.")
                        else:
                                return render_template("index.html", error="Please fill out all of the fields.")
                else:
                        return render_template("index.html", error="That is not a valid activation URL.")

@app.route('/login', methods=['POST','GET'])
def login():
	if request.method == "POST":
		if request.form['password'] and request.form['username']:
			hashedPassword = hashPassword(request.form['password'])
			you = User.query.filter_by(username=request.form['username'], password=hashedPassword).first()
			if you:
				session['username'] = you.username
				session['name'] = you.name
                                session['user_id'] = you.id
                                session['account_id'] = you.account_id
                                session['teams'] = you.teams
                                session['email'] = you.email
				
				return redirect('/dashboard')
			else:
				return render_template('login.html', error="Invalid credentials, please try again.")
		else:
			return render_template('login.html', error="Please enter a username and password.")
	elif request.method == "GET":
		return render_template('login.html')

@app.route('/logout')
def logout():
	try:
		session.pop('username', None)
		session.pop('name', None)
		session.pop('user_id', None)
		session.pop('account_id', None)
		session.pop('teams', None)
		session.pop('email', None)
	
		return render_template('index.html', message="Successfully logged out.")
	except Exception, e:
		return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
	if request.method == "POST":
		if request.form['company_name'] and request.form['name'] and request.form['username'] and request.form['email'] and request.form['password'] and request.form['password_again']:
			if request.form['password'] == request.form['password_again']:
				# proceed
				print request.form['username']

				possibleID = random.randint(1,1000000)
				accountCheck = Account.query.filter_by(id=possibleID).first()

				while accountCheck:
					possibleID = random.randint(1,1000000)
					accountCheck = Account.query.filter_by(id=possibleID)

				password = hashPassword(request.form['password'])
				newAccount = Account(possibleID, request.form['company_name'], 0, "2999-12-31 23:59:59", 1)
				newUser = User(possibleID, request.form['name'], request.form['username'], password, request.form['email'], teams="")
				db.session.add(newAccount)
				db.session.add(newUser)
				db.session.commit()
				
				you = User.query.filter_by(username=request.form['username'], password=password, email=request.form['email']).first()
				session['username'] = request.form['username']
				session['name'] = request.form['name']
				session['user_id'] = you.id
				session['account_id'] = you.account_id
				session['teams'] = you.teams
				session['email'] = you.email
			
				return render_template('index.html', message="Account registered.")
					
			else:
				return render_template('register.html', error="The passwords did not match, please try again.")
		else:
			return render_template('register.html', error="Please fill out the entire form.")
	elif request.method == "GET":
		return render_template('register.html')

if __name__ == '__main__':
        app.run(host='0.0.0.0',debug=True)
