# author: Luke McDaniel
# project: Senior Project
# purpose: Python Client
# description: This program is a python client that connects 
# to the flask servercit takes the username and session passcode 
# to get started


import os
import socketio
import json

connected = True

# enter your username that you use to log into the server
username = input("\nenter username: ")
name_space = '/' + username.replace(" ", "")

# enter the passcode seen on your home page after login
passcode = input("\nenter passcode: ")

# initialize client
sio = socketio.Client()

# lets you know you are connected to the namespace
@sio.event(namespace=name_space)
def connect():
	print('connected')

# sends verification data once connected to the namespace 
@sio.event(namespace=name_space)
def on_connect(msg):
	if msg["master"] is True:
		verifyData = {"namespace":name_space, "passcode":passcode, "sid":msg["sid"]}
		sio.emit('espTryVerify', verifyData, namespace='/lukemcdaniel')

# lets client know it is verified on namespace, start messaging protocol
@sio.on('espClientVerified', namespace=name_space)
def on_espClientVerified(msg):
	if msg["verified"] is True:
		messageProtocol()

# prints out messages received from web client
@sio.on('server_to_esp', namespace=name_space)
def on_server_to_esp(msg):
	print('\b\b\b\b\b\b\nreceived: \n' + msg + '\n\nsend: ')
	# end program if message was disconnect
	if msg == 'disconnect':
		sio.disconnect()
		connected = False
		os._exit(0)

# ends thread once disconnected from namespace
@sio.event(namespace=name_space)
def disconnect():
	print("I am disconnected!")
	os._exit(0)

# prompt user for a message, then send message
def messageProtocol():
	while (connected):
		my_message = input("\nsend: \n")
		sio.emit('esp_to_server', my_message, namespace=name_space)

# connect to namespace then let socket functionality control program
def main():
	sio.connect('http://localhost:5000', namespaces=[name_space])
	sio.wait()

if __name__ == "__main__":
	main()