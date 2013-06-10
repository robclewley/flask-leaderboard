from flask import session, render_template, redirect, url_for, flash, abort, request

from leaderboard import app, db
from leaderboard.database import Downvote
from leaderboard.filters import user_has_voted

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