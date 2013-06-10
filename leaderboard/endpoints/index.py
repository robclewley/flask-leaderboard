from flask import g, redirect, url_for, render_template

from leaderboard import app
from leaderboard.database import Entry, User, Task
from leaderboard.filters import get_score

@app.route('/')
def leaderboard():
    if not g.user:
        return redirect(url_for('login'))
    entries = Entry.query.all()
    users = User.query.all()
    sorted_users = sorted(users, key=lambda user: get_score(user.id), reverse=True)
    tasks = Task.query.all()
    return render_template('index.html', entries=entries, users=sorted_users, tasks=tasks)