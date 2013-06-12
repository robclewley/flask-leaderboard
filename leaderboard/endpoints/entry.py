from flask import session, abort, request, flash, redirect, url_for, render_template

from leaderboard import app, db
from leaderboard.database import User, Task, Entry

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