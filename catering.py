"""
	So You Think You Can Cater
	CS 1520 Fall 2017 Assignment 3
	Jordan Grogan
	Tu/Th 6:00 Lecture / Th 7:30 Recitation
"""

from flask import Flask, request, session, url_for, redirect, render_template, flash
from models import db, User, Event

app = Flask(__name__)

app.secret_key = "this is a terrible secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catering.db'
db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
	"""Creates the database tables."""
	db.drop_all()
	db.create_all()
	print('Initialized the database.')

# by default, direct to login
@app.route("/", methods=['GET', 'POST'])
def default():
	"""Default page."""

	if "username" in session:
		user = User.query.get(session['user_id'])

		if request.method == 'POST' and session['role'] == 2:
			# Add an Event
			if not request.form['name']:
				flash("Please enter an event name.")
			elif not request.form['date']:
				flash("Please enter an event date.")
			elif Event.query.filter_by(date = request.form['date']).count() > 0:
				flash("Sorry, that date is not available.")
			else:
				db.session.add(Event(name=request.form['name'], date=request.form['date'], customer_id=user.id))
				db.session.commit()
				flash("Your event has been added!")

		if session['role'] == 0: # Owner
			events = Event.query.all()
			return render_template('default_owner.html', events=events)
		elif session['role'] == 1: # Staff
			yourevents = user.staffer_events
			unfilledevents = Event.query.filter(~Event.staffers.contains(user)).all() # only show events that the user is not already working
			unfilledevents = [event for event in unfilledevents if len(event.staffers) < 3] # only show events with less than 3 staffers signed up
			return render_template('default_staff.html', yourevents=yourevents, unfilledevents=unfilledevents)
		elif session['role'] == 2: # Customer
			yourevents = user.customer_events
			return render_template('default_customer.html', yourevents=yourevents)

	return redirect(url_for('login'))

@app.route("/login", methods=['GET', 'POST'])
def login():
	"""Logs the user in."""

	# first check if the user is already logged in
	if "username" in session:
		flash("Already logged in!")
		return redirect(url_for('default'))

	# if not, and the incoming request is via POST try to log them in
	elif request.method == 'POST':
		if request.form['username'] == "owner" and request.form['password'] == "pass":
			session['user_id'] = 0
			session['username'] = "owner"
			session['role'] = 0
			return redirect(url_for('default'))
		else:
			user = User.query.filter_by(username=request.form['username']).first()
			if user is None:
				flash("Invalid username, please try again.")
			elif user.password != request.form['password']:
				flash("Invalid password, please try again.")
			else:
				session['user_id'] = user.id
				session['username'] = user.username
				session['role'] = user.role
				return redirect(url_for('default'))

	return render_template('login.html')

@app.route("/logout")
def logout():
	"""Logs the user out."""

	# if logged in, log out, otherwise offer to log in
	if "username" in session:
		session.clear()
		flash("Successfully logged out!")
	else:
		flash("Not currently logged in!")

	return redirect(url_for("login"))

@app.route('/register', methods=['GET', 'POST'])
def register():
	"""Registers the user."""

	if "username" in session:
		return redirect(url_for('default'))

	if request.method == 'POST':
		if not request.form['username']:
			flash("Please enter a username.")
		elif not request.form['password']:
			flash("Plase enter a password.")
		elif User.query.filter_by(username = request.form['username']).count() > 0:
			flash("Sorry, that username is already taken.")
		else:
			db.session.add(User(username=request.form['username'], password=request.form['password'], role=2))
			db.session.commit()
			flash("You were successfully registered and can login now.")
			return redirect(url_for('login'))
	return render_template('register.html')

@app.route('/cancel')
def cancel():
	"""Cancel an event."""

	if request.args.get('event'):
		if Event.query.get(request.args.get('event')).customer_id == session['user_id']:
			ename = Event.query.get(request.args.get('event')).name
			db.session.delete(Event.query.get(request.args.get('event')))
			db.session.commit()
			flash("{} has been cancelled.".format(ename))
		else:
			flash("You do not have permission to cancel that event.")
	else:
		flash("Error getting event.")

	return redirect(url_for('default'))

@app.route('/addstaff', methods=['GET', 'POST'])
def addstaff():
	"""Owner can add staff."""

	if "username" not in session or session['role'] != 0:
		flash("You do not have permission to access that page.")
		return redirect(url_for('default'))
	else:
		if request.method == 'POST':
			if not request.form['username']:
				flash("Please enter a username.")
			elif not request.form['password']:
				flash("Plase enter a password.")
			elif User.query.filter_by(username = request.form['username']).count() > 0:
				flash("Sorry, that username is already taken.")
			else:
				db.session.add(User(username=request.form['username'], password=request.form['password'], role=1))
				db.session.commit()
				flash("That staffer was successfully added and can login now.")
				return redirect(url_for('default'))
		return render_template('addstaff.html')

@app.route('/signup')
def signup():
	"""Staff can sign up for an event."""

	if request.args.get('event') and session['role'] == 1:
		event = Event.query.get(request.args.get('event'))
		event.staffers.append(User.query.get(session['user_id']))
		db.session.commit()
		flash("You are now signed up for {}.".format(event.name))
	else:
		flash("Error getting event.")

	return redirect(url_for('default'))
