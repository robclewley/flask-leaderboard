import os
import sys

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
base_dir = os.path.dirname(os.path.abspath(__file__))

if os.path.exists(os.path.join(base_dir, 'app.cfg')):
    app.config.from_pyfile(os.path.join(base_dir, 'app.cfg'))
elif os.path.exists(os.path.join(base_dir, '../app.cfg')):
    app.config.from_pyfile(os.path.join(base_dir, '../app.cfg'))
else:
    raise IOError('Could not find app.cfg')

db = SQLAlchemy(app)

import leaderboard.endpoints