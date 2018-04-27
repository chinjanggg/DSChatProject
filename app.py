import functools
from flask import Flask, session, render_template, request
from flask_login import current_user
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

if __name__ == '__main__':
	socketio.run(app)

@socketio.on('connect')
def connect():
	if current_user.is_authenticated:
		emit('my response', 
		{'message': '{0} has joined'.format(current_user.name)},
		broadcast=True)
	else:
		return render_template('login.html')

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped		

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

@socketio.on('join')
@authenticated_only
def on_join(data):
	username = data['username']
	room = data['room']
	join_room(room)
	send(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
	username = data['username']
	room = data['room']
	leave_room(room)
	send(username + ' has left the room.', room=room)

def ack():
	print('read')
	
@socketio.on('send_message',)
def send_message(message):
	user = flask.session.get('user')
	group = flask.session.get('group')
	now = datetime.datetime.now().replace(microsecond=0).isoformat()
	emit('send message',(now, user, group, message), namespace='/chat', callback=ack, broadcast=true)
	
@socketio.on('receive_message')
def handle_message(msg):
	print('received: ' + str(msg))
