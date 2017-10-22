from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

schedules = db.Table('schedules',
	db.Column('staffer_id', db.Integer, db.ForeignKey('user.id')),
	db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(80), unique=True)
	password = db.Column(db.String(120))
	role = db.Column(db.Integer) # staffer = 1 / customer = 2
	customer_events = db.relationship('Event', backref='customer')
	staffer_events = db.relationship('Event', secondary=schedules, lazy=True, backref=db.backref('staffers', lazy="select"))

	def __init__(self, username, password, role):
		self.username = username
		self.password = password
		self.role = role

	def __repr__(self):
		return '<User {}>'.format(self.username)

class Event(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	date = db.Column(db.String(50))
	customer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __init__(self, name, date, customer_id):
		self.name = name
		self.date = date
		self.customer_id = customer_id

	def __repr__(self):
		return '<Event {} ({})>'.format(self.name, self.date)
