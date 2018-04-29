import functools
from flask import Flask, session, redirect, request, render_template, url_for
from flask_login import current_user, LoginManager, login_required, login_user, logout_user, UserMixin
from flaskext.mysql import MySQL
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect, send
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['MYSQL_DATABASE_USER'] = 'ds_chat'
app.config['MYSQL_DATABASE_PASSWORD'] = 'alchemy'
app.config['MYSQL_DATABASE_DB'] = 'ds_chat'
mysql = MySQL()
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()
#cursor.execute('select * from client')
#data = cursor.fetchone() / cursor.fetchall()

@socketio.on('connect')
def connect():
	if current_user.is_authenticated:
		emit('my response',
		{'message': '{0} has joined'.format(current_user.name)},
		broadcast=True)
	else:
		return render_template('login.html')

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

@socketio.on('join')
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
	print('message sent')

@socketio.on('send_message')
def send_message(message, user, time):
	time = time.replace(microsecond=0).isoformat()
	user = str(user)
	message = user + ': ' + message + ' (' + time + ')'
	send(message, callback=ack, broadcast=True)#, room=room)

@socketio.on('message')
def handle_message(message):
	user = session.get('user')
	now = datetime.datetime.now()
	print('received: ' + str(message), user, now)
	send_message(message, user, now)

class User(UserMixin):
	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
	def check_password(self, password):
		return check_password_hash(self.password_hash, password)
	
@login_manager.user_loader
def load_user(user_id):
	return User.get(user_id)
	
class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Login')
	
@app.route('/login/', methods=['GET', 'POST'])
def login():
	'''cursor.execute('select * from client')
	data = list(cursor.fetchall())
	print(data)
	for d in data:
		print(d[0])
	if current_user.is_authenticated:
		return redirect(url_for('chat'))'''
	form = LoginForm()
	if form.validate_on_submit():
		'''user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))'''
		#login_user(user)
		return redirect(url_for('chat'))
	return render_template('login.html', form=form)

@app.route('/logout/')
@login_required
def logout():
	logout_user()
	return redirect('/')
	
@app.route('/chat/')
@login_required
def chat():
	return render_template('chat.html')

@app.route('/')
def index():
	if current_user.is_authenticated:
		return redirect(url_for('chat'))
	else:
		return redirect(url_for('login'))

if __name__ == '__main__':
	socketio.run(app)
