from flask import Flask, session, g
from db import db
import bcrypt
from friends import *
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired

app = Flask(__name__)
app.config.from_object('config')

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(255), nullable=False)
	last_name = db.Column(db.String(255), nullable=False)
	username = db.Column(db.String(255), unique=True, index=True, nullable=False)
	password_hash = db.Column(db.String(255), index=True, nullable=False)
	admin = db.Column(db.Boolean, default=False, nullable=False)
	posts = db.relationship('Post', backref='user')
	comments = db.relationship('Comment', backref='user')
	verified = db.Column(db.Boolean, default=False, nullable=False)
	email = db.Column(db.String(255), unique=True, nullable=False)
	sent_requests = db.relationship('FriendshipRequest', backref='sender', primaryjoin=(FriendshipRequest.requesting_id==id))
	received_requests = db.relationship('FriendshipRequest', backref='receiver', primaryjoin=(FriendshipRequest.requested_id==id))
	friends = db.relationship('User', secondary=friendships,
			primaryjoin=(friendships.c.friend_id1==id),
			secondaryjoin=(friendships.c.friend_id2==id))

	def verify_password(self, password):
		return bcrypt.hashpw(password.encode('utf-8'), self.password_hash.encode('utf-8')) == self.password_hash
	
	def login(self, password):
		if self.verify_password(password) and self.verified:
			token = self.gentoken()
			session['token'] = token
			g.current_user = self
			return True
		return None

	def gentoken(self):
		serializer = Serializer(app.config['SECRET_KEY'], expires_in=3600)
		return serializer.dumps({'user_id':self.id})
	
	def verify(self):
		self.verified = True
		try:
			db.session.add(self)
			db.session.commit()
		except:
			db.session.rollback()

	def make_friend(self, friend):
		try:
			self.friends.append(friend)
			friend.friends.append(self)
			db.session.add(self, friend)
			db.session.commit()
		except:
			db.session.rollback()
	
	@classmethod
	def from_user_id(cls, user_id):
		return cls.query.filter(cls.user_id == user_id).first()

	@classmethod 
	def from_username(cls, username):
		return cls.query.filter(cls.username == username).first()

	@classmethod 
	def from_email(cls, email):
		return cls.query.filter(cls.email == email).first()

	@classmethod
	def create(cls, **kwargs):
		kwargs['password_hash'] = bcrypt.hashpw(kwargs['password'].encode('utf-8'), bcrypt.gensalt())
		del kwargs['password']
		user = cls(**kwargs)
		db.session.add(user)
		db.session.commit()
		return user

	@classmethod
	def from_token(cls, token):
		serializer = Serializer(app.config['SECRET_KEY'])
		try:
			data = serializer.loads(token)
		except SignatureExpired, BadSignature:
			return None
		if data['user_id']:
			return cls.query.get(data['user_id'])	
		return None
		



