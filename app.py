#HW: make a user home page that shows personal info about the user and shows friends--**
#HW: make a friendship request table, once request is accepted/rejected delete it from table--**
#HW: we want to be able to share and comment on pictures.
#HW: make it possible to accept friend requests(make a page to show sent and received requests with a user route)

#HW: if user does not exist create user from FB_ID, Find way to connect existing user to FB_ID

from db import db
from flask import Blueprint, flash, Flask, g, redirect, render_template, request, session, abort, Markup
from models import *
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from blueprints import *
from helpers import *
import bcrypt


app = Flask(__name__)
app.config.from_object('config')

db.create_all()

def gen_csrf_token():
	if '_csrf_token' not in session:
		session['_csrf_token'] = bcrypt.gensalt()
	return session['_csrf_token']

def csrf_helper():
	token = gen_csrf_token()
	return Markup('<input type="hidden" name="_csrf_token" value="{0}" />'.format(token))


app.jinja_env.globals['csrf_helper'] = csrf_helper

@app.before_request
def csrf_protect():
	if request.method == 'POST':
		token = session.pop('_csrf_token', None)
		form_token = request.form.get('_csrf_token')
		if not token or not form_token or token != form_token:
			abort(403)

@app.route('/')
def home():
	user = current_user()
	username = None
	oauth_link = 'https://www.facebook.com/dialog/oauth?client_id={0}&redirect_uri={1}'.format(app.config['FB_APP_ID'], app.config['FB_REDIRECT_URI'])
	if user:
		username = user.username
	return render_template('home.html', username=username, current_user=user, oauth_link=oauth_link)


app.register_blueprint(auth.auth, session=session, g=g)
app.register_blueprint(user.user, session=session, g=g)

if __name__ == '__main__':
	app.run()