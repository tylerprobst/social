from flask.ext.sqlalchemy import SQLAlchemy
import MySQLdb
from flask import Flask

app = Flask(__name__)
app.config.from_object('config')

db = SQLAlchemy(app)
