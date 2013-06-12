from flask import session, abort, render_template

from leaderboard import app
from leaderboard.database import Entry
from leaderboard.filters import get_user_name

@app.route('/profile/<id>')
def profile(id):
	if 'user_id' not in session:
		abort(401)
	name = get_user_name(id)
	entries = Entry.query.filter(Entry.receiver == id)
	return render_template('profile.html', entries=entries, name=name, id=id)