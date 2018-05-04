import requests
from flask import Flask
app = Flask(__name__)

@app.route('/')
def check():
    server1running = True
    try:
        requests.get('http://127.0.0.1:5001')
    except requests.exceptions.ConnectionError: 
        server1running = False
    if server1running:
        return 'Use server 1'
        
    server2running = True
    try:
        requests.get('http://127.0.0.1:5002')
    except requests.exceptions.ConnectionError: 
        server2running = False
    if server2running:
        return 'Use server 2'

    return 'Both servers are not available'

@app.route('/hello')
def hello():
    try:
        content = requests.get('http://127.0.0.1:5001/hello').content
    except requests.exceptions.ConnectionError:
        try:
            content = requests.get('http://127.0.0.1:5002/hello').content
        except requests.exceptions.ConnectionError:
            return 'Both servers are not available'
    return content