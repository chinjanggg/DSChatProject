import functools
from flask import Flask, session, redirect, request, render_template, url_for, flash
from flask_login import current_user, LoginManager, login_required, login_user, logout_user, UserMixin
from flaskext.mysql import MySQL
from flask_socketio import SocketIO, emit, disconnect, send, join_room, leave_room
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

@socketio.on('connect')
def connect():
	if current_user.is_authenticated:
		print('{0} has joined'.format(current_user.name))
	else:
		return render_template('login.html')

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')

@socketio.on('join')
def on_join(group):
	user = current_user.id
	cursor.execute("call joinGroup('" + user + "', '" + group + "');")
	join_room(group)
	session['group_id'] = group
	now = datetime.datetime.now()
	send_message(current_user.name + ' has joined the group.', 'System', now, group)
	break_group(user, group)

@socketio.on('leave')
def on_leave(group):
	user = current_user.id
	now = datetime.datetime.now()
	send_message(current_user.name + ' has left the group.', 'System', now, session.get(group_id))
	cursor.execute("call leaveGroup('" + user + "', '" + group + "');")
	leave_room(group)
	session['group_id'] = 'x'
	
@socketio.on('switch')
def on_switch(group):
	old_group = session.get('group_id')
	break_group(old_group)
	cancel_break(group)
	session['group_id'] = group
	send_unread(current_user.id, group)
	
def break_group(user, group):
	leave_room(group)
	cursor.execute("call breakGroup('" + user + "', '" + group + "');")
	
def cancel_break(user, group):
	join_room(group)
	cursor.execute("call cancelBreak('" + user + "', '" + group + "');")

def send_message(message, user, time, group):
	time = time.replace(microsecond=0).isoformat()
	user = string(user)
	emit('message', (message, user, time), broadcast=True, room=group)

@socketio.on('message')
def handle_message(message):
	user = current_user.id
	group = session.get('group')
	now = datetime.datetime.now()
	print('received: ' + str(message), user, now)
	send_message(message, current_user.name, now, group)
	cursor.execute("call storeMessage('" + user + "', '" + group + "', '" + message + "');")

def send_unread():
	cursor.execute("call getUnread('" + user + "', '" + group + "');")
	unread = cursor.fetchall()
	for msg in unread:
		time = msg[1].replace(microsecond=0).isoformat()
		cursor.execute("select DisplayName from Client where CID = '" + msg[3] + "';")
		user = cursor.fetchone()
		send_message(msg[2], user, time, group)

class User(UserMixin):
	def __init__(self, id, name):
		self.id = id
		self.name = name
	'''def set_password(self, password):
		self.password_hash = generate_password_hash(password)
	def check_password(self, password):
		return check_password_hash(self.password_hash, password)'''
	
@login_manager.user_loader
def load_user(user_id):
	inst = "select * from client where cid='" + user_id + "';"
	cursor.execute(inst)
	data = cursor.fetchone()
	return User(data[0], data[1])
	
class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Login')
	
@app.route('/login/', methods=['GET', 'POST'])
def login():
	cursor.execute('select * from client')
	data = cursor.fetchone()
	if current_user.is_authenticated:
		return redirect(url_for('chat'))
	form = LoginForm()
	if form.validate_on_submit():
		inst = "select * from client where cid='" + form.username.data
		inst += "' and password='" + form.password.data + "';"
		# password shouldn't be sent in plain-text
		cursor.execute(inst)
		user_entry = cursor.fetchone()
		if user_entry is None:
			print('invalid')
			flash('Invalid username or password')
			return redirect(url_for('login'))
		user = load_user(user_entry[0])
		login_user(user)
		session['group_id'] = 'x'
		return redirect(url_for('chat'))
		
	return render_template('login.html', form=form)

@app.route('/logout/')
@login_required
def logout():
	user = current_user.id
	group = session.get('group_id')
	#break_group(user, group)
	logout_user()
	session['group_id'] = 'x'
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
