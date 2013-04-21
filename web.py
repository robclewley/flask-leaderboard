from __future__ import with_statement
import time
import os, re
from sqlite3 import dbapi2 as sqlite3
from hashlib import md5
from datetime import datetime
from flask import Flask, request, session, url_for, redirect, \
     render_template, abort, g, flash, _app_ctx_stack
from werkzeug import check_password_hash, generate_password_hash, secure_filename



UPLOAD_FOLDER = 'static/img'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif', 'mp4'])

DATABASE = 'gnar'
SECRET_KEY = 'flaskofgnar'

app = Flask(__name__)
app.config.from_object(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_db():
	top = _app_ctx_stack.top
	if not hasattr(top, 'sqlite_db'):
		top.sqlite_db = sqlite3.connect(app.config['DATABASE'])
		top.sqlite_db.row_factory = sqlite3.Row
	return top.sqlite_db

@app.teardown_appcontext
def close_database(exception):
	top = _app_ctx_stack.top
	if hasattr(top, 'sqlite_db'):
		top.sqlite_db.close()

#def init_db():
#	with app.app_context():
#		db = get_db()
#		with app.open_resource('schema.sql') as f:
#			db.cursor().executescript(f.read())
#		db.commit()

def query_db(query, args=(), one=False):
	cur = get_db().execute(query, args)
	rv = cur.fetchall()
	return (rv[0] if rv else None) if one else rv
	
def get_user_id(username):
	rv = query_db('select user_id from user where username = ?',
					[username], one=True)
	return rv[0] if rv else None

###### TEMPLATE FILTERS ########

@app.template_filter('format_datetime')
def format_datetime(timestamp):
	return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

@app.template_filter('get_user_name')
def get_user_name(id):
	rv = query_db('select username from user where user_id = ?',
					[id], one=True)
	return rv[0] if rv else None

def get_task_id(title):
	rv = query_db('select task_id from task where title = ?',
					[title], one=True)
	return rv[0] if rv else None

@app.template_filter('get_task_title')
def get_task_title(id):
	rv = query_db('select title from task where task_id = ?',
					[id], one=True)
	return rv[0] if rv else None
	
@app.template_filter('get_approval_status')
def get_approval_status(approval):
	if approval == None:
		return '<a href="/entry/?/approve">RED</a>'
	else:
		rv = query_db('select sender from approval where approval_id = ?',
					[approval], one=True)
		return True, get_user_name(rv[0])

@app.template_filter('profile_link')
def profile_link(username):
	return '<a href="/profile/' + str(get_user_id(username)) + '">' + username + '</a>'

@app.before_request
def before_request():
	g.user = None
	if 'user_id' in session:
		g.user = query_db('select * from user where user_id = ?',
							[session['user_id']], one=True)

@app.route('/')
def leaderboard():
	if not g.user:
		return redirect(url_for('login'))
	entries = query_db('SELECT * FROM entry')
	users = query_db('select * from user order by user.score desc ')
	tasks = query_db('select * from task')
	return render_template('leaderboard.html', entries=entries, users=users, tasks=tasks)

@app.route('/profile/<id>')
def profile(id):
	name = get_user_name(id)
	entries = query_db('SELECT * FROM entry where receiver = ?',
							[id])
	score = query_db('SELECT score from user where user_id = ?',
							[id])[0][0]
	return render_template('profile.html', entries=entries, score=score, name=name)

@app.route('/entry/<id>/approve', methods=['GET'])
def add_approval(id):
	if 'user_id' not in session:
		abort(401)
	if request.method == 'GET':
		db = get_db()
		lv = query_db('select approval from entry where entry_id = ?',
						[id], one=True)
		if lv[0] != None:
			flash('that entry has already been approved...')
			return redirect(url_for('leaderboard'))
		else:
			db.execute('insert into approval (entry, sender) values (?, ?)',
						(id, session['user_id']))
			rv = query_db('select approval_id from approval where entry = ?',
						[id], one=True)
			db.execute('UPDATE entry SET approval=? WHERE entry_id = ?',
						(rv[0], id))
			dv = query_db('select task.value from task, entry where task_id = entry.task',
						one=True)
			db.execute('UPDATE user SET score=score+? WHERE user_id = ?',
						(dv[0], id))
			db.commit()
			flash('you approved this entry...')
			return redirect(url_for('leaderboard'))

@app.route('/entry/add', methods=['GET', 'POST'])
def add_entry():
	if 'user_id' not in session:
		abort(401)
	users = query_db('select * from user')
	tasks = query_db('select * from task')
	if request.method == 'POST':
		db = get_db()
		if request.files['file']:
			file = request.files['file']
			if file and allowed_file(file.filename):
				filename = str(time.time()) + secure_filename(file.filename)
				file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
				db.execute('insert into entry (sender, receiver, task, datetime, proof) values (?, ?, ?, ?, ?)',
						(session['user_id'], request.form['receiver'], request.form['task'], int(time.time()), filename ))
				db.commit()
				return redirect(url_for('leaderboard'))
		else:
			db.execute('insert into entry (sender, receiver, task, datetime) values (?, ?, ?, ?)',
					(session['user_id'], request.form['receiver'], request.form['task'], int(time.time()) ))
			db.commit()
			return redirect(url_for('leaderboard'))
		flash('your entry was added...')
	return render_template('add_entry.html', users=users, tasks=tasks)

##### SESSION METHODS #####

@app.route('/register', methods=['GET', 'POST'])
def register():
	if g.user:
		return redirect(url_for('leaderboard'))
	error = None
	if request.method == 'POST':
		if not request.form['username']:
 			error = 'You have to enter a username'
		elif not request.form['email'] or \
			'@' not in request.form['email']:
			error = 'You have to enter a valid email address'
		elif not request.form['password']:
			error = 'You have to enter a password'
		elif request.form['password'] != request.form['password2']:
			error = 'The two passwords do not match'
		elif get_user_id(request.form['username']) is not None:
 			error = 'The username is already taken'
		else:
			db = get_db()
			db.execute('insert into user (username, email, pw_hash, score) values (?, ?, ?, ?)',
				[request.form['username'], request.form['email'],
				generate_password_hash(request.form['password']), 0])
			db.commit()
			flash('You were successfully registered and can login now')
			return redirect(url_for('login'))
	return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if g.user:
		return redirect(url_for('leaderboard'))
	error = None
	if request.method == 'POST':
		user = query_db('select * from user where username = ?', [request.form['username']], one=True)
		if user is None:
			error = 'Invalid username'
		elif not check_password_hash(user['pw_hash'], request.form['password']):
			error = 'Invalid password'
		else:
			flash('You were logged in')
			session['user_id'] = user['user_id']
			return redirect(url_for('leaderboard'))
	return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	flash('You were logged out')
	session.pop('user_id', None)
	return redirect(url_for('leaderboard'))
	
if __name__ == '__main__':
	#init_db()
	app.run(debug=True)