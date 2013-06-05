from datetime import datetime

from app import app
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, unique=True)
	email = db.Column(db.String, unique=True)
	pw_hash = db.Column(db.String)

	def __init__(self, name, email, pw_hash):
		self.name = name
		self.email = email
		self.pw_hash = pw_hash
		
	def __getitem__(self, item):
		return (self.id, self.name, self.email, self.pw_hash)[item]

class Task(db.Model):
	__tablename__ = 'tasks'
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String)
	description = db.Column(db.String)
	value = db.Column(db.Integer)
	
	def __init__(self, title, description, value):
		self.title = title
		self.description = description
		self.value = value
	
class Entry(db.Model):
	__tablename__ = 'entries'
	id = db.Column(db.Integer, primary_key=True)
	pub_date = db.Column(db.DateTime)

	sender = db.Column(db.Integer, db.ForeignKey('users.id'))
	receiver = db.Column(db.Integer, db.ForeignKey('users.id'))
	task = db.Column(db.Integer, db.ForeignKey('tasks.id'))
	
	attachments = db.relationship('Attachment', backref='entries', lazy='dynamic')
	upvotes = db.relationship('Upvote', backref='entries', lazy='dynamic')
	downvotes = db.relationship('Downvote', backref='entires', lazy='dynamic')
	
	def __init__(self, sender, receiver, task):
		self.pub_date = datetime.now()
		self.sender = sender
		self.receiver = receiver
		self.task = task

class Upvote(db.Model):
	__tablename__ = 'upvotes'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	entry_id = db.Column(db.Integer, db.ForeignKey('entries.id'))
	
	def __init__(self, user_id, entry_id):
		self.user_id = user_id
		self.entry_id = entry_id
	
class Downvote(db.Model):
	__tablename__ = 'downvotes'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	entry_id = db.Column(db.Integer, db.ForeignKey('entries.id'))

	def __init__(self, user, entry):
		self.user_id = user_id
		self.entry_id = entry_id
		
class Attachment(db.Model):
	__tablename__ = 'attachments'
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
	entry_id = db.Column(db.Integer, db.ForeignKey('entries.id'))
	url = db.Column(db.String)
	
	def __init__(self, user_id, entry_id, url):
		self.user_id = user_id
		self.entry_id = entry_id
		self.url = url