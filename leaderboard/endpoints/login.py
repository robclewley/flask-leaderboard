from werkzeug import check_password_hash
from flask import g, redirect, url_for, request, session, flash, render_template

from leaderboard import app
from leaderboard.database import User

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