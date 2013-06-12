import os
import time

from werkzeug import secure_filename
from flask import session, abort, request, flash, redirect, url_for, render_template

from leaderboard import app, db
from leaderboard.database import Attachment
from leaderboard.filters import allowed_file

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