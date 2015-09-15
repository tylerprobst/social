from functools import wraps
from flask import g, session, redirect, flash
from models import User

def current_user():
	current_user = g.get('current_user')
	if not current_user:
		token = session.get('token')
		if token:
			current_user = User.from_token(token)
	g.current_user = current_user	
	return current_user

def logged_in(func):
	@wraps(func)
	def decorated(*args, **kwargs):
		if current_user():
			return func(*args, **kwargs)
		else:
			flash('You must be logged in!')
			return redirect('/login')
	return decorated