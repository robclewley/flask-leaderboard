import config

from flask import Flask

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = config.ALLOWED_EXTENSIONS