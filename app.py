import flask
import os
from flask import Flask, flash, redirect, render_template, \
     request, url_for
from markupsafe import escape   
from flask_sqlalchemy import SQLAlchemy
import flask_login
from werkzeug.security import generate_password_hash, check_password_hash
import dotenv

dotenv.load_dotenv()
SECRET_VAR = os.getenv("SECRET_VAR")

app = Flask(__name__)
#need secret key for when flashing messages
app.secret_key = '@?nGUAl$K6_$V+%S' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)


class CarListing(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    make = db.Column(db.String(30), nullable = False)
    model = db.Column(db.String(30), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    mileage = db.Column(db.Integer, nullable = False)
    #foreign key to link user to listing
    user_id =  db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"ID : {self.id} Make: {self.make} Model: {self.model} Price: {self.price}  Mileage: {self.mileage} user_id: {self.user_id}"

class User(flask_login.UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), unique = True)
    hashed_password = db.Column(db.String(30), nullable = False)
    is_admin = db.Column(db.Boolean, default = False)
    #users can have many posts
    listings = db.relationship('CarListing', backref='owner') 


    def __repr__(self):
        return f"ID : {self.id} Username: {self.username}"
    
    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)


    #used to check if the password is correct
    def check_password(self, password):
        return check_password_hash(self.hashed_password, password )
    def set_admin(self):
        self.is_admin=True


#list of cars which creates each row of the table 
cars = [{"Make" : "Mazda", "Model" : "Mazda2", "Price" : 2495, "Mileage": 87434},
        {"Make" : "Honda", "Model" : "Jazz", "Price" : 3795, "Mileage": 99873},
        {"Make" : "Toyota", "Model" : "Corolla", "Price" : 2200, "Mileage": 102224},
        {"Make" : "Suzuki", "Model" : "Swift", "Price" : 2250, "Mileage": 113000}]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def valid_car(make, model, price, mileage):
    #method to check if a car entry is valid (input validation)
    error_msg=None
    is_valid = False
    
    try:
        #try converting price to int if it's a non-integer string it will fail
        price = int(price)
    except ValueError:
        error_msg = "Price must be an integer value"
        #render the add page again with the error
        return error_msg, is_valid
    try:
        #try converting mileage to int, if it's a non-integer string it fails
        mileage = int(mileage)
    except ValueError:
        error_msg = "Mileage must be an integer value"
        #render add page with the error
        return error_msg, is_valid
    #checking that none of the values are 'None'
    if not make or not model or not price or not mileage:
        error_msg = "You cannot submit an empty form, please complete every field"
        return error_msg, is_valid
    elif make == "" or make.isspace() == True:
        error_msg="Make cannot be empty or contain whitespace"
        return error_msg, is_valid
    elif model == "" or model.isspace() == True:
        error_msg="Model cannot be empty"
        #checking that price is a positive integer
        return error_msg, is_valid
    elif price <=0:
        error_msg= 'Price must be an integer value greater than 0'
        return error_msg, is_valid
    elif mileage <=0:
        error_msg = 'Mileage must be an integer value greater than 0'
        print(error_msg)
        return error_msg, is_valid
    else:
        is_valid = True
        return error_msg, is_valid



def populate_db():
        #check if database already has data if empty populate it
        if CarListing.query.first() !=None:
            print("Car database already has data")
        else:
            for car in cars:
                car_entry = CarListing(make=car["Make"].capitalize(), model=car["Model"], price=car["Price"], mileage=car["Mileage"], user_id = 0)
                with app.app_context():
                    
                    db.session.add(car_entry)
                    db.session.commit()

@app.route("/")
def index():
    return render_template('index.html', page_name="home")


@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == "POST":

        user = User.query.filter_by(username = request.form.get('username').lower()).one_or_none()
        
        if user is None or user.check_password(request.form.get('password')) == False:
            print("LOGIN FAILED")

            error_msg=("Your login was unsuccessful, please try again")
            return render_template("login.html", error = error_msg)
        else:
            print("LOGIN SUCCESSFUL")
            
            flask_login.login_user(user)
            flash(f'Login Successful welcome {flask_login.current_user.username.capitalize()}!', 'success')
            return redirect(url_for("profile"))
    return render_template('login.html', page_name = "login")

@app.route('/profile')
@flask_login.login_required
def profile():
    return render_template('profile.html', page_name = "profile")

@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    flash('Log out successful', 'success')
    return redirect(url_for('login'))

@app.route('/signup', methods=['POST','GET'])
def signup():
    #signup method to allow users to signup
    if request.method == "POST":
        #get the inputs 
        error = None
        user_inp = request.form.get("Username")
        print(user_inp)
        user_inp = user_inp.lower() #normalise all usernames to lowercase
        password_inp = request.form.get("Password")
        print(password_inp)
        print(len(password_inp))
        #some validation for the inputs
        if user_inp == None or password_inp == None:
            error = "INPUT CANNOT BE NONE"
        elif user_inp == "" or user_inp.isspace() ==True:
            error = "USERNAME CANNOT BE EMPTY OR CONTAIN WHITESPACE"
        elif password_inp == "" or password_inp.isspace() ==True:
            error = "PASSWORD CANNOT BE EMPTY OR CONTAIN WHITESPACE"
        elif len(password_inp) < 8:
            error = "PASSWORD MUST BE AT LEAST 8 CHARACTERS LONG"
        
        else:

        #check if a user already exists for a given username
            if User.query.filter_by(username = user_inp).one_or_none() == None:
                #if a user doesn't exist we can create it 
                new_user = User(username = user_inp)
                new_user.set_password(request.form.get("Password"))
                print(new_user)
                print("ADDING USER")
                db.session.add(new_user)
                db.session.commit()
                #flashing a message to give feedback to the user
                flash('User successfully added to the system please login', 'success')
                return redirect(url_for("login"))
            else:
                print("NOT ADDING")
                error = "CANNOT ADD THIS USER TO THE DATABASE, AS ANOTHER USER ALREADY EXISTS WITH THIS USERNAME"
            
        return render_template('signup.html', error=error)

    return render_template('signup.html', page_name = "signup")


@app.route('/user/<username>')
def show_user_profile(username):
    return f'User {escape(username)}'

@app.route('/health')
def health():
    return 'OK'

@app.route('/edit/<int:car_id>', methods=['POST','GET'])
@flask_login.login_required
def edit_car(car_id):
    #method to allow editing a car entry
    old_car_entry = CarListing.query.get(car_id)
    #check if current user owns the listing or if they're an admin and then allow editing
    if flask_login.current_user.id == old_car_entry.owner.id or flask_login.current_user.is_admin:
        if request.method =="POST":
            #if a form is submit get data from the form
            new_make = request.form.get("Make").strip()
            new_model = request.form.get("Model").strip()
            new_price = request.form.get("Price")
            new_mileage = request.form.get("Mileage")
            print(new_make, new_model, new_price, new_mileage)
            error_msg, is_valid = valid_car(new_make, new_model, new_price, new_mileage)
            if is_valid:
                #if the car passes validation update the listing
                old_car_entry.make = new_make.capitalize()
                old_car_entry.model = new_model
                old_car_entry.price = new_price
                old_car_entry.mileage = new_mileage
                db.session.commit()
                flash(f'Vehicle with ID: {car_id} was successfully edited', 'success') #flashing a message for when the user is redirected
                return redirect(url_for("show_cars"))
            else:
                #if not valid return the page with the error message
                return render_template('edit.html', error=error_msg, id=car_id, car=old_car_entry)
    else:
        flash('UNAUTHORISED YOU CANNOT EDIT THIS LISTING', 'danger')
        return redirect(url_for('show_cars'))

   
   

        #rendered on the GET request
    return render_template('edit.html', id = car_id, car=old_car_entry, page_name = "edit")
#route for deleting cars using variable route
@app.route('/delete/<int:car_id>', methods=['POST','GET'])
@flask_login.login_required
def delete_car(car_id):

    #implement logic for deleting from the database where car.id is car_id
    car_entry = CarListing.query.get(car_id)
    print(car_entry)
    print(car_entry.owner.id)
    #check if current user owns the listing or if they're an admin
    if flask_login.current_user.id == car_entry.owner.id or flask_login.current_user.is_admin:
        db.session.delete(car_entry)
        db.session.commit()
        print(car_entry)
        flash(f'Vehicle with ID: {car_id} successfully Deleted', 'success') #flashing a message for when the user is redirected
        return redirect(url_for("show_cars"))
    else:
        flash(f'You cannot remove this post', 'danger')
        cars_db = CarListing.query.all()
        return(render_template('cars.html', car_list = cars_db))
@app.route('/cars')
def show_cars():
    action_tab = False
    #using first() instead of one_or_none because first doesn't raise an exception when multiple rows exist
    if flask_login.current_user.is_authenticated and CarListing.query.filter_by(user_id = flask_login.current_user.id).first() != None:
        action_tab = True
    cars_db = CarListing.query.all()
    return render_template('cars.html', car_list = cars_db, action_tab = action_tab, page_name = "cars")

@app.route('/add', methods=['POST','GET'])
def add_cars():
    if flask_login.current_user.is_authenticated:
        if request.method == "POST":
            #if user has submitted a form extract data from it
            #strip() to clean up user input before adding to the system
            owner = flask_login.current_user.id
            make = request.form.get("Make").strip()
            model = request.form.get("Model").strip()
            price = request.form.get("Price").strip()
            mileage = request.form.get("Mileage").strip()

            error_msg, is_valid = valid_car(make, model, price, mileage)
            if is_valid:
                #if car is valid it can be added to the database
                car_db_entry = CarListing(make=make.capitalize(), model=model, price=price, mileage=mileage, user_id = owner)
                with app.app_context():
                        db.session.add(car_db_entry)
                        db.session.commit()
                flash('Vehicle successfully added', 'success') #flashing a message for when the user is redirected
                return redirect(url_for("show_cars"))
            else:
                return render_template('add.html', error=error_msg)
    else:
        flash('You must login or sign up to sell cars', 'danger')
        return redirect(url_for("login"))
    return render_template('add.html', page_name = "add") #when user clicks on the route ('GET') render the add page

if __name__ ==("__main__"):
    #database is only created if a database doesn't already exist
    #this also prevents my fake data from being duplicated in the database
    with app.app_context():
        db.create_all() #create the database and tables
        populate_db()    
        print("test")
        #if users exist in the database we dont need to set up the admin and SYSTEM account
        if User.query.first() !=None:
            print("Already have users setup")
        else:
            #setup the SYSTEM and admin account
            user_entry = User(id=0, username="SYSTEM")
            user_entry.set_password('n/a')
            admin_entry = User(username='admin', is_admin = True)
            admin_entry.set_password(SECRET_VAR)
            db.session.add(user_entry)
            print("SYSTEM ADDED")
            db.session.add(admin_entry)
            print("ADMIN ADDED")
            db.session.commit()
            print("SYSTEM AND ADMIN ACCOUNTS SETUP")
    print("app running now ")
    app.run(debug=True)    

# with app.test_request_context():
#     print(url_for('index'))
#     print(url_for('login'))
#     print(url_for('login', next='/'))
#     print(url_for('show_user_profile', username = 'John Doe'))
