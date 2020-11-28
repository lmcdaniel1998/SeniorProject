# author: Luke McDaniel
# project: Senior Project
# purpose: Database Object Definition
# description: This file defines the two objects contained in our database.
# The user and the post, users and posts are related by the user id as a foreign key


# werkzeug us used to encrypt passwords in the database so the actual password text
# string can never be accessed
from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# user has an id, username, email, password hash, and a list of posts
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    # user is represented by its username
    def __repr__(self):
        return '<User {}>'.format(self.username)

    # creates a hash for the password and stores in database
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # checks if password matches password in database with hash
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# allows flask server to access user object in database
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# post has an id, body text, time stamp, and user id foreign key
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    # post is represented by its body text
    def __repr__(self):
        return '<Post {}>'.format(self.body)
