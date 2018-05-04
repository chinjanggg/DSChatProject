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
	cursor = conn.cursor()
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
	now = datetime.datetime.now()
	send_message(current_user.name + ' has joined the group.', 'System', now, group)
	cursor.execute("call breakGroup('" + user + "', '" + group + "');")
	conn.commit()
	cursor.close()
	return redirect(url_for('chat'))

@socketio.on('leave')
def on_leave(data):
	cursor = conn.cursor()
	user = current_user.id
	group = data['group']
	now = datetime.datetime.now()
	send_message(current_user.name + ' has left the group.', 'System', now, session.get(group_id))
	cursor.execute("call leaveGroup('" + user + "', '" + group + "');")
	conn.commit()
	leave_room(group)
	session['group_id'] = 'x'
	cursor.close()

@socketio.on('switch')
def on_switch(data):
	cursor = conn.cursor()
	user = current_user.id
	group = data['group']
	old_group = session.get('group_id')
	if old_group != 'x':
		leave_room(old_group)
		cursor.execute("call breakGroup('" + user + "', '" + old_group + "');")
	redirect('chat')
	join_room(group)
	cursor.execute("call cancelBreak('" + user + "', '" + group + "');")
	conn.commit()
	session['group_id'] = group
	cursor.close()
	
@socketio.on('break')
def on_break():
	cursor = conn.cursor()
	old_group = session.get('group_id')
	leave_room(old_group)
	cursor.execute("call breakGroup('" + current_user.id + "', '" + old_group + "');")
	cursor.close()

def send_message(message, user, time, group):
	time = time.replace(microsecond=0).isoformat()
	emit('message', (message, user, time), broadcast=True, room=group)

@socketio.on('message')
def handle_message(message):
	cursor = conn.cursor()
	user = current_user.id
	group = str(session.get('group'))
	now = datetime.datetime.now()
	print('received: ' + str(message), user, now)
	send_message(message, current_user.name, now, group)
	if str(group) == 'None':
		print('group not found')
		flash('Group not found')
		cursor.close()
		return
	cursor.execute("call storeMessage('" + user + "', '" + group + "', '" + message + "');")
	cursor.close()

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
	cursor = conn.cursor()
	inst = "select * from client where cid='" + user_id + "';"
	cursor.execute(inst)
	data = cursor.fetchone()
	cursor.close()
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
		cursor = conn.cursor()
		# password shouldn't be sent in plain-text
		cursor.execute('select CID, Password from Client;')
		for entry in cursor.fetchall():
			if entry[0] == form.username.data and entry[1] == form.password.data:
				login_user(load_user(form.username.data))
				session['group_id'] = 'x'
				cursor.close()
				return redirect(url_for('chat'))
		print('invalid')
		flash('Invalid username or password')
		cursor.close()
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
		cursor = conn.cursor()
		cursor.execute('select CID from Client;')
		for entry in cursor.fetchall():
			if entry[0] == username:
				flash('Duplicated username')
				cursor.close()
				return render_template('register.html', form=form)
		cursor.execute("call createUser('" + username + "', '" + form.reg_dpname.data + "', '" + form.reg_password.data + "');")
		conn.commit()
		cursor.close()
		return redirect('/')
	return render_template('register.html', form=form)
	
class CreateGroupForm(FlaskForm):
	group_id = StringField('Group ID', validators=[DataRequired()])
	group_name = StringField('Group Name', validators=[DataRequired()])
	submit = SubmitField('Create')

def getGroupList(user):
	cursor = conn.cursor()
	cursor.execute('select * from ClientInGroup;')
	group_set = set()
	for entry in cursor.fetchall():
		if entry[0] == user:
			group_set.add(entry[1])
	cursor.execute('select GID, GName from CGroup;')
	group_list = []
	for entry in cursor.fetchall():
		if entry[0] in group_set:
			group_list.append((entry[0], entry[1]))
	cursor.close()
	return group_list
	
def getUnread(user, group):
	cursor = conn.cursor()
	cursor.execute("call getUnread('" + user + "', '" + group + "');")
	unread = cursor.fetchall()
	messages = []
	for msg in unread:
		time = msg[1].replace(microsecond=0).isoformat()
		cursor.execute("select DisplayName from Client where CID = '" + msg[3] + "';")
		user = cursor.fetchone()[0]
		messages.append((user, msg[2], time))
	cursor.close()
	return messages
	
def getRead(user, group):
	cursor = conn.cursor()
	cursor.execute("call getMessage('" + user + "', '" + group + "');")
	read = cursor.fetchall()
	messages = []
	for msg in read:
		time = msg[1].replace(microsecond=0).isoformat()
		cursor.execute("select DisplayName from Client where CID = '" + msg[3] + "';")
		user = cursor.fetchone()[0]
		messages.append((user, msg[2], time))
	cursor.close()
	return messages
	
@app.route('/chat/', methods=['GET', 'POST'])
@login_required
def chat():
	form = CreateGroupForm()
	if form.validate_on_submit():
		cursor = conn.cursor()
		group_id = form.group_id.data
		cursor.execute('select GID from CGroup;')
		for entry in cursor.fetchall():
			if entry[0] == group_id:
				flash('Duplicated group ID')
				return render_template('chat.html', form=form, group_list=group_list)
		cursor.execute("call createGroup('" + group_id + "', '" + form.group_name.data + "');")
		conn.commit()
		cursor.close()
		on_join({'group':group_id})
	user = current_user.id
	group = str(session.get('group'))
	print('groupid:', group)
	return render_template('chat.html', form=form, group_list=getGroupList(user), unread=getUnread(user, group), read=getRead(user, group))

@app.route('/')
def index():
	if current_user.is_authenticated:
		return redirect(url_for('chat'))
	else:
		return redirect(url_for('login'))

if __name__ == '__main__':
	socketio.run(app)