"""
	So You Think You Can Cater
	CS 1520 Fall 2017 Assignment 3
	Jordan Grogan
	Tu/Th 6:00 Lecture / Th 7:30 Recitation
"""

from flask import Flask, request, session, url_for, redirect, render_template, flash
from models import db, Customer, Staffer, Event

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///catering.db'
db.init_app(app)

@app.cli.command('initdb')
def initdb_command():
	"""Creates the database tables."""
	db.drop_all()
	db.create_all()
	print('Initialized the database.')

@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Logs the user in."""
	if g.user:
		return redirect(url_for('timeline'))
	error = None
	if request.method == 'POST':

		user = User.query.filter_by(username=request.form['username']).first()
		if user is None:
			error = 'Invalid username'
		elif not check_password_hash(user.pw_hash, request.form['password']):
			error = 'Invalid password'
		else:
			flash('You were logged in')
			session['user_id'] = user.user_id
			return redirect(url_for('timeline'))
	return render_template('login.html', error=error)
