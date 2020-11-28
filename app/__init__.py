# author: Luke McDaniel
# project: Senior Project
# purpose: Initializes Flask Server
# description: imports many of the libraries used by the server
# initializes app, database, login manager, bootstrap, and web socket


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config

from flask_bootstrap import Bootstrap

from flask_socketio import SocketIO, send, emit, join_room, leave_room, \
    Namespace, disconnect

from flask_session import Session

app = Flask(__name__)							# creates flask app
app.config.from_object(Config)					# use config to establish secret key and database directory
db = SQLAlchemy(app)							# use SQLAlchemny library as database manager
migrate = Migrate(app, db)						# migrage is used to make changes to database structure
login = LoginManager(app)						# initialize login manager for site
login.login_view = 'login'

bootstrap = Bootstrap(app)						# boostrap is used for css styles

app.config['SESSION_TYPE'] = 'filesystem'		# log session information in file system

# flask-socketio
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=True) # must allow cors origins to use libraries in javascript

from app import routes, models

