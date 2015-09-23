from flask import Blueprint, flash, Flask, g, redirect, render_template, request, session
from models import *
from helpers import *

user = Blueprint("user", __name__)

app = Flask(__name__)
app.config.from_object('config')

@user.route('/friends')
def friends():
	return render_template('friends.html', user=current_user())

@user.route('/users', methods=['GET'])
@logged_in
def index():
	return render_template('users.html', users=filter(lambda x: x.id != g.current_user.id, User.query.all()))

@user.route('/requests', methods=['GET', 'POST'])
@logged_in
def requests():
	if request.method == 'GET':
		pending_requests = FriendshipRequest.query.filter_by(requesting_id=g.current_user.id)
		sent_requests = FriendshipRequest.query.filter_by(requested_id=g.current_user.id)
		return render_template('requests.html', pending_requests=pending_requests, sent_requests=sent_requests)
	elif request.method == 'POST':
		friend_id = request.form.get('friend_id')
		FriendshipRequest.send_request(g.current_user.id, friend_id)
		flash('Friend request sent')
		return redirect('/')

@user.route('/requests/cancel', methods=['POST'])
@logged_in
def cancel():
	request_id = request.form.get('request_id')
	friendshiprequest = FriendshipRequest.from_id(request_id)
	friendshiprequest.delete()
	flash('Request Deleted')
	return redirect('/')

@user.route('/requests/accept', methods=['POST'])
@logged_in
def accept():
	request_id = request.form.get('request_id')
	friendshiprequest = FriendshipRequest.from_id(request_id)
	friendshiprequest.accept()
	flash('Request Accepted')
	return redirect('/friends')
