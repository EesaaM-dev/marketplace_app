from flask import Flask
from flask import url_for
from flask import request
from markupsafe import escape   
app = Flask(__name__)

@app.route("/")
def index():
    return 'Index Page'

@app.route('/hello')
def hello():
    return 'Hello, World'



@app.route('/login', methods=['GET','POST'])
def login():
    return 'login'

@app.route('/user/<username>')
def show_user_profile(username):
    return f'User {escape(username)}'

@app.route('/health')
def health():
    return 'OK'


with app.test_request_context():
    print(url_for('index'))
    print(url_for('login'))
    print(url_for('login', next='/'))
    print(url_for('show_user_profile', username = 'John Doe'))



