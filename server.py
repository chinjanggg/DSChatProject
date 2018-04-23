from flask import Flask, session
from flask_socketio import SocketIO, emit

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

if __name__ == '__main__':
	socketio.run(app)
	
@socketio.on('chat_message', namespace='/test')
def handle_chat_message(msg):
	print('received: ' + str(msg))