import os, time

from app import app
from werkzeug import check_password_hash, generate_password_hash, secure_filename
from flask import request, session, url_for, redirect, \
     render_template, abort, g, flash

from models import db, User, Task, Entry, Upvote, Downvote, Attachment
from filters import *

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = User.query.filter(User.id == session['user_id']).first()

@app.route('/')
def leaderboard():
	if not g.user:
		return redirect(url_for('login'))
	entries = Entry.query.all()
	users = User.query.all()
	sorted_users = sorted(users, key=lambda user: get_score(user.id), reverse=True)
	tasks = Task.query.all()
	return render_template('leaderboard.html', entries=entries, users=sorted_users, tasks=tasks)

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
			session['user_id'] = user.id
			flash('You were logged in')
			return redirect(url_for('leaderboard'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	session.pop('user_id', None)
	flash('You were logged out')
	return redirect(url_for('leaderboard'))