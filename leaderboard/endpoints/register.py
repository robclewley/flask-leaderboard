from werkzeug import generate_password_hash
from flask import g, redirect, url_for, request, flash, render_template

from leaderboard import app, db
from leaderboard.database import User

@app.route('/register', methods=['GET', 'POST'])
def register():
    if g.user:
        return redirect(url_for('leaderboard'))
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a name'
        elif not request.form['email'] or '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        else:
            user = User(request.form['username'], request.form['email'], generate_password_hash(request.form['password']))
            db.session.add(user)
            db.session.commit()
            flash('You were successfully registered and can login now')
            return redirect(url_for('login'))
    return render_template('register.html', error=error)