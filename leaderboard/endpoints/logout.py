from flask import session, flash, render_template, url_for

from leaderboard import app

@app.route('/logout')
def logout():
	session.pop('user_id', None)
	flash('You were logged out')
	return render_template('login.html')