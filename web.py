from __future__ import with_statement
import time
import os, re
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash, secure_filename

from flask.ext.sqlalchemy import SQLAlchemy

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif'])

SECRET_KEY = 'flaskofngar'

app = Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gnar'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)

class User(db.Model):
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
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String)
	description = db.Column(db.String)
	value = db.Column(db.Integer)
	
	def __init__(self, title, description, value):
		self.title = title
		self.description = description
		self.value = value
	
class Entry(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	pub_date = db.Column(db.DateTime)

	sender = db.Column(db.Integer, db.ForeignKey('user.id'))
	receiver = db.Column(db.Integer, db.ForeignKey('user.id'))
	task = db.Column(db.Integer, db.ForeignKey('task.id'))
	
	attachments = db.relationship('Attachment', backref='entry', lazy='dynamic')
	
	def __init__(self, sender, receiver, task):
		self.pub_date = datetime.now()
		self.sender = sender
		self.receiver = receiver
		self.task = task

class Upvote(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.Integer, db.ForeignKey('user.id'))
	entry = db.Column(db.Integer, db.ForeignKey('user.id'))
	
	def __init__(self, user, entry):
		self.user = user
		self.entry = entry
	
class Downvote(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user = db.Column(db.Integer, db.ForeignKey('user.id'))
	entry = db.Column(db.Integer, db.ForeignKey('user.id'))

	def __init__(self, user, entry):
		self.user = user
		self.entry = entry
		
class Attachment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'))
	url = db.Column(db.String)
	
	def __init__(self, user_id, entry_id, url):
		self.user_id = user_id
		self.entry_id = entry_id
		self.url = url

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
	
def user_has_voted(user, entry):
	has_upvotes = Upvote.query.filter(Upvote.user == user, Upvote.entry == entry).first()
	has_downvotes = Downvote.query.filter(Downvote.user == user, Downvote.entry == entry).first()
	if has_upvotes != None or has_downvotes != None:
		return True
	else:
		return False
		
def get_task_value(id):
	score = Task.query.filter(Task.id == id).first().value
	return score

###### TEMPLATE FILTERS ########

@app.template_filter('get_user_name')
def get_user_name(id):
	return User.query.filter(User.id == id).first().name

@app.template_filter('get_task_title')
def get_task_title(id):
	return Task.query.filter(Task.id == id).first().title
	
@app.template_filter('get_score')
def get_score(id):
	score = 0
	entries = Entry.query.filter(Entry.receiver == id)
	for entry in entries:
		upvotes = Upvote.query.filter(Upvote.entry == entry.id).count()
		downvotes = Downvote.query.filter(Downvote.entry == entry.id).count()
		if upvotes > downvotes:
			score += get_task_value(entry.task)
	return score
	
@app.template_filter('format_datetime')
def format_datetime(timestamp):
	return timestamp.strftime('%Y-%m-%d @ %H:%M')

################################

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter(User.id == session['user_id']).first()

######## VIEW FUNCTIONS ########

@app.route('/')
def leaderboard():
	if not g.user:
		return redirect(url_for('login'))
	entries = Entry.query.all()
	x = User.query.all()
	users = sorted(x, key=lambda x: get_score(x.id), reverse=True)
	tasks = Task.query.all()
	return render_template('leaderboard.html', entries=entries, users=users, tasks=tasks)

@app.route('/profile/<id>')
def profile(id):
	name = get_user_name(id)
	entries = Entry.query.filter(Entry.receiver == id)
	return render_template('profile.html', entries=entries, name=name, id=id)

@app.route('/entry/<id>/upload', methods=['GET', 'POST'])
def add_attachment(id):
	if 'user_id' not in session:
		abort(401)
	filename = None
	if request.method == 'POST' and request.files['file']:
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = str(time.time()) + secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			attachment = Attachment(session['user_id'], id, filename)
			db.session.add(attachment)
			db.session.commit()
			flash('your attachment was uploaded')
			return redirect(url_for('leaderboard'))
		else:
			flash('invalid file')
			return redirect(url_for('leaderboard'))
	return render_template('add_attachment.html', id=id)

@app.route('/entry/<id>/upvote', methods=['GET'])
def upvote(id):
	if 'user_id' not in session:
		abort(401)
	if request.method == 'GET':
		if user_has_voted(session['user_id'], id):
			flash('you have already voted on this entry')
			return redirect(url_for('leaderboard'))
		else:
			upvote = Upvote(session['user_id'], id)
			db.session.add(upvote)
			db.session.commit()
			flash('upvoted entry')
			return redirect(url_for('leaderboard'))
			
@app.route('/entry/<id>/downvote', methods=['GET'])
def downvote(id):
	if 'user_id' not in session:
		abort(401)
	if request.method == 'GET':
		if user_has_voted(session['user_id'], id):
			flash('you have already voted on this entry')
			return redirect(url_for('leaderboard'))
		else:
			downvote = Downvote(session['user_id'], id)
			db.session.add(downvote)
			db.session.commit()
			flash('downvoted entry')
			return redirect(url_for('leaderboard'))

@app.route('/entry/add', methods=['GET', 'POST'])
def add_entry():
	if 'user_id' not in session:
		abort(401)
	users = User.query.all()
	tasks = Task.query.all()
	if request.method == 'POST':
		if not request.form['receiver']:
			flash('you must specify a player')
			return redirect(url_for('add_entry'))
		if not request.form['task']:
			flash('you must specify a task')
			return redirect(url_for('add_entry'))
		entry = Entry(session['user_id'], request.form['receiver'], request.form['task'])
		db.session.add(entry)
		db.session.commit()
		flash('entry added...')
		return redirect(url_for('leaderboard'))
	return render_template('add_entry.html', users=users, tasks=tasks)

##### SESSION METHODS #####

@app.route('/register', methods=['GET', 'POST'])
def register():
	if g.user:
		return redirect(url_for('leaderboard'))
	error = None
	if request.method == 'POST':
		if not request.form['username']:
 			error = 'You have to enter a name'
		elif not request.form['email'] or \
			'@' not in request.form['email']:
			error = 'You have to enter a valid email address'
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		else:
			user = User(request.form['username'], request.form['email'],
					generate_password_hash(request.form['password']))
			db.session.add(user)
			db.session.commit()
			flash('You were successfully registered and can login now')
			return redirect(url_for('login'))
	return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if g.user:
		return redirect(url_for('leaderboard'))
	error = None
	if request.method == 'POST':
		user = User.query.filter(User.name == request.form['username']).first()
		if user is None:
			error = 'Invalid username'
		elif not check_password_hash(user.pw_hash, request.form['password']):
			error = 'Invalid password'
		else:
			flash('You were logged in')
			session['user_id'] = user.id
			return redirect(url_for('leaderboard'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('user_id', None)
	flash('You were logged out')
	return redirect(url_for('leaderboard'))
	
if __name__ == '__main__':
	app.run(debug=True)