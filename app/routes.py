# author: Luke McDaniel
# project: Senior Project
# purpose: Contains Site Routing and Web Socket Protocols
# description: This is the most crutial file for the server functionality.
# It contains the routes for all site pages. ie how you go from login to index.
# It also contains all of the the websocket fuctioality for the server.


from flask import render_template, flash, redirect, url_for, request, session, json as flask_json
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db, socketio
from app.forms import LoginForm, RegistrationForm
from app.models import User


# server socket io stuff
import json
import eventlet
from flask_socketio import SocketIO, send, emit, join_room, leave_room, \
    Namespace, disconnect


# index is the "home" page for users, create namespace for user here and load index.html
@app.route('/')
@app.route('/index')
@login_required
def index():
    # remove spaces and add forward slash to create namespace
    temp_namespace = "/" + (current_user.username).replace(" ", "")
    # create a namespace for a user profile
    socketio.on_namespace(MyNamespace(temp_namespace))
    return render_template('index.html', title='Home')

# this is the first page you see when visiting the site. Users can login here or go to registration page
@app.route('/login', methods=['GET', 'POST'])
def login():
    # if user is already authenticated (remember me was checked) go directly to index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # load login form
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        # if user can't be logged in, stay on login page for another login attempt
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # if user can be logged in redirect to index page
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

# this page is simple, it just logs out the user
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# if you want to create a new user navigate to this page from the login page
@app.route('/register', methods=['GET', 'POST'])
def register():
    # if user is already logged in, just redirect to index
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    # load registration form
    form = RegistrationForm()
    if form.validate_on_submit():
        # create user object and add to database
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        # after user is created you must log it in at login page
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)



# name spaces are used to create a secure channel for a user and its clients
# if a client is not registered on the namespace it cannot send or receive messages
# to other clients on the namespace
class MyNamespace(Namespace):

    # this class inherits from the namespace class in flask-socketIO
    def __init__(self, namespace):
        super(Namespace, self).__init__(namespace)
        self.ns = namespace                             # stores text name of namespace
        self.passcode = 'XXXXXX'                        # 6 digit session passcode set by web client
        self.master = False                             # indicates if namespace has a master or not
        self.primarySid = ""                            # stores sid of web client (controls namespace)
        self.sidList = []                               # sotres sid's of all clients verified on namespace

    # simple print to show if user connecting to namespace is verified
    # user_authenticated method is not working properly
    def connect(self):
        print('connect before authenticate')
        if not self.authenticate(request.args):
            print('not authenticate')
        else:
            print('authenticate')

    # starts verification sequence for when a new client connects to namespace
    def on_connect(self):
        print(current_user)
        if self.master is False:                # if namespace has no master start master verification sequence
            # user.is_authenticated is not working properly. When working should wrap everything inside of first if statement
            #if current_user.is_authenticated:   # if no master incomming connection must be authenticated 
            if request.args.get('fail'):
                return False
            print('authenticated sid: ' + request.sid)
            # send ns, sid, and master to web client
            data = {"namespace":self.ns, "sid":request.sid, "master":self.master}
            socketio.emit('on_web_connect', data, namespace=self.ns)
        else:                                   # if namespace has master start client verification sequence
            if request.args.get('fail'):
                    return False
            print('connecting sid: ' + request.sid)
            # send ns, sid, and master to client
            data = {"namespace":self.ns, "sid":request.sid, "master":self.master}
            socketio.emit('on_connect', data, namespace=self.ns)
    
    # when a user disconnects remove its sid from the sidList so that no unregistered clients can use that sid to join namespace
    # if master disconnects reset master fields
    def on_disconnect(self):
        if str(request.sid) == self.primarySid:
                self.primarySid = ""
                self.master = False
                self.passcode = 'XXXXXX'
                (self.sidList).clear()
        if request.sid in self.sidList:
            (self.sidList).remove(request.sid)

    # after on_web_connect web client will send the session passcode and its sid to server
    def on_establishWebMaster(self, data):
        retData = json.loads(data)                                          # parse json
        # this sid will become primary sid and have control over namespace
        if retData["master"] is True:
            self.master = True
            self.passcode = retData["passcode"]
            self.primarySid = retData["masterSid"]
            self.sidList.append(retData["masterSid"])

    # after on_connect client will send passcode to register itself on the namespace
    def on_espTryVerify(self, data):
        # check if passcode is correct
        if (self.passcode) == (data["passcode"]) and (self.ns) == (data["namespace"]):
            # add sid to registered sid list and send confirmation of verification
            self.sidList.append(data["sid"])
            # let client know it has been verified on the server
            confData = {"verified":True, "sid":request.sid}
            socketio.emit('espClientVerified', confData, namespace=self.ns)

    # receives a message from the esp client and forwards the message to the web client
    def on_esp_to_server(self, msg):
        # check if esp sending message is registered with namespace
        if request.sid in self.sidList:
            emit('server_to_web', msg, namespace=self.ns, broadcast=True)
            print(msg)

    # receives a message from the web client and forwards the message to all esp clients
    def on_web_to_server(self, msg):
        # check if web sending message is registered as master of namespace
        if request.sid in self.sidList and request.sid == self.primarySid:
            emit('server_to_esp', msg, namespace=self.ns, broadcast=True)
            print(msg)

    # destroys namespace on exit
    def on_exit(self, data):
        disconnect()
