from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Customer(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(100), nullable=False, unique=True)
	password = db.Column(db.String(100), nullable=False)

	events = db.relationship('Event', backref='customer')

	def __init__(self, username, password):
		self.username = username
		self.password = password

	def __repr__(self):
		return '<Customer {}>'.format(self.username)

schedules = db.Table('schedules',
	db.Column('staffer_id', db.Integer, db.ForeignKey('staffer.id')),
	db.Column('event_id', db.Integer, db.ForeignKey('event.id'))
)

class Staffer(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(24), nullable=False)
	password = db.Column(db.String(64), nullable=False)

	events = db.relationship('Event', secondary=schedules, backref=db.backref('staffers', lazy='dynamic'))

	def __init__(self, username, email, pw_hash):
		self.username = username
		self.pw_hash = pw_hash

	def __repr__(self):
		return '<Staffer {}>'.format(self.username)

class Event(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50))
	date = db.Column(db.String(50))
	customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

	def __init__(self, name, date):
		self.name = name
		self.date = date

	def __repr__(self):
		return '<Event {} ({})>'.format(self.username, self.date)
