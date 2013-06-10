from flask import session, abort, request, flash, redirect, url_for, render_template

from leaderboard import app, db
from leaderboard.database import Upvote
from leaderboard.filters import user_has_voted

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