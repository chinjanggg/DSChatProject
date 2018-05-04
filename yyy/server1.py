from flask import Flask
app = Flask(__name__)

@app.route('/')
def check():
    return 'Server 1 Running'

@app.route('/hello')
def hello():
    return 'Hello from server 1'