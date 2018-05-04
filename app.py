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
def on_join(data):
	user = current_user.id
	group = data['group']
	cursor.execute('select GID from CGroup;')
	found = False
	for entry in cursor.fetchall():
		if entry[0] == group:
			found = True
	if not found:
		flash('Group ID not found')
		return redirect(url_for('chat'))
	cursor.execute("call joinGroup('" + user + "', '" + group + "');")
	session['group_id'] = group
	now = datetime.datetime.now()
	send_message(current_user.name + ' has joined the group.', 'System', now, group)
	cursor.execute("call breakGroup('" + user + "', '" + group + "');")
	conn.commit()

@socketio.on('leave')
def on_leave(data):
	user = current_user.id
	group = data['group']
	now = datetime.datetime.now()
	send_message(current_user.name + ' has left the group.', 'System', now, session.get(group_id))
	cursor.execute("call leaveGroup('" + user + "', '" + group + "');")
	conn.commit()
	leave_room(group)
	session['group_id'] = 'x'

@socketio.on('switch')
def on_switch(data):
	user = current_user.id
	group = data['group']
	old_group = session.get('group_id')
	if old_group != 'x':
		leave_room(old_group)
		cursor.execute("call breakGroup('" + user + "', '" + old_group + "');")
	join_room(group)
	cursor.execute("call cancelBreak('" + user + "', '" + group + "');")
	conn.commit()
	session['group_id'] = group
	send_unread(user, group)
	
@socketio.on('break')
def on_break():
	old_group = session.get('group_id')
	leave_room(old_group)
	cursor.execute("call breakGroup('" + current_user.id + "', '" + old_group + "');")

def send_message(message, user, time, group):
	time = time.replace(microsecond=0).isoformat()
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
		user = cursor.fetchone()[0]
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
	if current_user.is_authenticated:
		return redirect(url_for('chat'))
	form = LoginForm()
	if form.validate_on_submit():		
		# password shouldn't be sent in plain-text
		cursor.execute('select CID, Password from Client;')
		for entry in cursor.fetchall():
			if entry[0] == form.username.data and entry[1] == form.password.data:
				login_user(load_user(form.username.data))
				session['group_id'] = 'x'
				return redirect(url_for('chat'))
		print('invalid')
		flash('Invalid username or password')
	return render_template('login.html', form=form)

@app.route('/logout/')
@login_required
def logout():
	logout_user()
	session['group_id'] = 'x'
	return redirect('/')

class RegisterForm(FlaskForm):
	reg_username = StringField('Username', validators=[DataRequired()])
	reg_dpname = StringField('Display Name', validators=[DataRequired()])
	reg_password = PasswordField('Password', validators=[DataRequired()])
	reg_repassword = PasswordField('Reenter Password', validators=[DataRequired()])
	submit = SubmitField('Register')
	
@app.route('/register/', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		if form.reg_password.data != form.reg_repassword.data:
			flash('Passwords not matched')
			return render_template('register.html', form=form)
		username = form.reg_username.data
		cursor.execute('select CID from Client;')
		for entry in cursor.fetchall():
			if entry[0] == username:
				flash('Duplicated username')
				return render_template('register.html', form=form)
		cursor.execute("call createUser('" + username + "', '" + form.reg_dpname.data + "', '" + form.reg_password.data + "');")
		conn.commit()
		return redirect('/')
	return render_template('register.html', form=form)
	
class CreateGroupForm(FlaskForm):
	group_id = StringField('Group ID', validators=[DataRequired()])
	group_name = StringField('Group Name', validators=[DataRequired()])
	submit = SubmitField('Create')
	
@app.route('/chat/', methods=['GET', 'POST'])
@login_required
def chat():
	form = CreateGroupForm()
	if form.validate_on_submit():
		group_id = form.group_id.data
		cursor.execute('select GID from CGroup;')
		for entry in cursor.fetchall():
			if entry[0] == group_id:
				flash('Duplicated group ID')
				return render_template('chat.html', form=form)
		cursor.execute("call createGroup('" + group_id + "', '" + form.group_name.data + "');")
		conn.commit()
	cursor.execute('select * from ClientInGroup;')
	group_set = set()
	for entry in cursor.fetchall():
		if entry[0] == current_user.id:
			group_set.add(entry[1])
	cursor.execute('select GID, GName from CGroup;')
	group_list = []
	for entry in cursor.fetchall():
		if entry[0] in group_set:
			group_list.append((entry[0], entry[1]))
	return render_template('chat.html', form=form, group_list=group_list)

@app.route('/')
def index():
	if current_user.is_authenticated:
		return redirect(url_for('chat'))
	else:
		return redirect(url_for('login'))

if __name__ == '__main__':
	socketio.run(app)