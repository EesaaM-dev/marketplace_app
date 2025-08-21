from flask import Flask
from flask import url_for
from flask import request
from flask import render_template
from markupsafe import escape   
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    return 'login'

@app.route('/user/<username>')
def show_user_profile(username):
    return f'User {escape(username)}'

@app.route('/health')
def health():
    return 'OK'

@app.route('/cars')
def show_cars():
    return render_template('cars.html')

@app.route('/add')
def add_cars():
    return render_template('add.html')

if __name__ ==("__main__"):
    app.run(debug=True)

# with app.test_request_context():
#     print(url_for('index'))
#     print(url_for('login'))
#     print(url_for('login', next='/'))
#     print(url_for('show_user_profile', username = 'John Doe'))



