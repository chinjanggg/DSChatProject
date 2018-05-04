import requests
from flask import Flask
app = Flask(__name__)

@app.route('/')
def check():
    try:
        r = requests.get('http://127.0.0.1:5000')
    except requests.exceptions.ConnectionError: 
        return 'Server 2 Running'
    return 'Server 2 Not Running'