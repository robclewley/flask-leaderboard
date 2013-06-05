import os
_basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
SECRET_KEY = 'flaskofgnar'

UPLOAD_FOLDER = 'static/attachments'
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'gif'])

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'scavenger.db')
DATABASE_CONNECTION_OPTIONS = {}

THREADS_PER_PAGE = 8