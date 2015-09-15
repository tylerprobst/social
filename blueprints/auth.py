from db import db
from flask import Blueprint, flash, Flask, g, redirect, render_template, request, session
from flask_mail import Message, Mail
from models import *
from sqlalchemy.exc import IntegrityError, InvalidRequestError

auth = Blueprint("auth", __name__)


app = Flask(__name__)
app.config.from_object('config')

mail = Mail(app)

@auth.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	if request.method == 'GET':
		return render_template('login.html')
	elif request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		user = User.from_email(email)
		if user and user.login(password):
			session['user_id'] = user.id
			flash('You were successfully logged in')
			return redirect('/')
		else:
			flash('Login failed, please try again')
			return redirect('/login')

@auth.route('/logout', methods=['POST'])
def logout():
	session['token'] = None
	flash('You have sucessfully logged out.')
	return redirect('/')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'GET':
		return render_template('/signup.html')
	elif request.method == 'POST':
		#try:
		first_name = request.form.get('first_name')
		last_name = request.form.get('last_name')
		username = request.form.get('username')
		email = request.form.get('email')
		confirm_email = request.form.get('confirm_email')
		password = request.form.get('password')
		confirm_password = request.form.get('confirm_password')
		if email != confirm_email:
			flash('Emails do not match, please try again.')
			return redirect('/signup')
		elif password != confirm_password:
			flash('Passwords do not match, please try again.')
			return redirect('/signup')
		else:
			user = User.create(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
			token = user.gentoken()
			link = 'http://localhost:5000/verify?token=' + token
			msg = Message('email works!', sender='tprobstcoding@gmail.com', recipients=['tprobstcoding@gmail.com'])
			msg.body = link
			mail.send(msg)
			flash('Confirmation email sent.')
		'''except IntegrityError:
			flash('That username/email is taken, please try again.')
			db.session.rollback()
			return redirect('/signup')
		except InvalidRequestError:
			flash('I\'m sorry, something went wrong, please try again.')
			db.session.rollback()
			return redirect('/signup')'''
		return redirect('/')

@auth.route('/verify')
def verify():
	token = request.args.get('token')
	user = User.from_token(token)
	if user:
		user.verify()
		flash('Your sign-up has been verified.')
		return redirect('/login')
	else:
		flash('Invalid verification link, please check your email, and try again.')
		return redirect('/') 
