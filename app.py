from flask import Flask, session, render_template
from flask_socketio import SocketIO, emit
import datetime

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

if __name__ == '__main__':
	socketio.run(app)

@socketio.on('connect')
def connect_handler():
	if current_user.is_authenticated:
		emit('my response', 
		{'message': '{0} has joined'.format(current_user.name)},
		broadcast=True)
	else:
		return render_template('login.html')
		
	
@socketio.on('send')
@authenticated_only
def send_message(message):
	user = flask.session.get('user')
	group = flask.session.get('group')
	now = datetime.datetime.now().replace(microsecond=0).isoformat()
	emit('send message',(now, user, group, message), namespace='/chat')