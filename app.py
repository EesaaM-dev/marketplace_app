import flask
import os
from enum import Enum
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

class Transmission(Enum):
    Manual = 1
    Automatic = 2

class BodyType(Enum):
    Convertible = 1
    Coupe = 2
    Estate = 3
    Hatchback = 4
    MPV = 5
    Saloon = 6
    SUV = 7

class FuelType(Enum):
    Petrol = 1
    Diesel = 2
    Electric = 3
    Hybrid = 4
class CarListing(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    make = db.Column(db.String(30), nullable = False)
    model = db.Column(db.String(30), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    mileage = db.Column(db.Integer, nullable = False)    
    transmission = db.Column(db.Enum(Transmission), nullable=False)
    fuel = db.Column(db.Enum(FuelType), nullable=False)
    body = db.Column(db.Enum(BodyType), nullable=False)
    year = db.Column(db.Integer, nullable = False)  


    #foreign key to link user to listing
    user_id =  db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"ID : {self.id} Make: {self.make} Model: {self.model} Price: {self.price}  Mileage: {self.mileage} user_id: {self.user_id} transmission: {self.transmission}"

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
cars = [{"Make" : "Mazda", "Model" : "Mazda2", "Price" : 2495, "Mileage": 87434, "Transmission" : Transmission.Manual, "Fuel" : FuelType.Petrol, "Body" : BodyType.Hatchback, "Year" : 2012 },
        {"Make" : "Honda", "Model" : "Jazz", "Price" : 3795, "Mileage": 99873, "Transmission" : Transmission.Manual, "Fuel" : FuelType.Petrol, "Body" : BodyType.Hatchback, "Year" : 2014 },
        {"Make" : "Toyota", "Model" : "Corolla", "Price" : 2200, "Mileage": 102224, "Transmission" : Transmission.Manual, "Fuel" : FuelType.Petrol, "Body" : BodyType.Hatchback, "Year" : 2005 },
        {"Make" : "Suzuki", "Model" : "Swift", "Price" : 2250, "Mileage": 69298, "Transmission" : Transmission.Manual, "Fuel" : FuelType.Petrol, "Body" : BodyType.Hatchback, "Year" : 2006 },
        {"Make" : "Toyota", "Model" : "Prius", "Price" : 5400, "Mileage": 74000, "Transmission" : Transmission.Automatic, "Fuel" : FuelType.Hybrid, "Body" : BodyType.Hatchback, "Year" : 2013 },
        {"Make" : "Toyota", "Model" : "Yaris", "Price" : 3200, "Mileage": 83000, "Transmission" : Transmission.Manual, "Fuel" : FuelType.Petrol, "Body" : BodyType.Hatchback, "Year" : 2013 },
        {"Make" : "Suzuki", "Model" : "Jimny", "Price" : 9890, "Mileage": 74000, "Transmission" : Transmission.Manual, "Fuel" : FuelType.Petrol, "Body" : BodyType.SUV, "Year" : 2012 },
        {"Make" : "Mazda", "Model" : "MX-5", "Price" : 14799, "Mileage": 33449, "Transmission" : Transmission.Manual, "Fuel" : FuelType.Petrol, "Body" : BodyType.Convertible, "Year" : 2018 },
        {"Make" : "Honda", "Model" : "Civic", "Price" : 3235, "Mileage": 79700, "Transmission" : Transmission.Manual, "Fuel" : FuelType.Petrol, "Body" : BodyType.Hatchback, "Year" : 2008 },
        {"Make" : "Toyota", "Model" : "Verso", "Price" : 2000, "Mileage": 120000, "Transmission" : Transmission.Manual, "Fuel" : FuelType.Diesel, "Body" : BodyType.MPV, "Year" : 2012 },
        {"Make" : "Tesla", "Model" : "Model 3", "Price" : 14995, "Mileage": 55000, "Transmission" : Transmission.Automatic, "Fuel" : FuelType.Electric, "Body" : BodyType.Saloon, "Year" : 2021 },
        ]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

def valid_car(make, model, price, mileage, transmission, fuel, body, year):
    #method to check if a car entry is valid (input validation)
    error_msg=None
    is_valid = False
    transmissions = [transmission.name for transmission in Transmission]
    body_types = [body_type.name for body_type in BodyType]
    fuel_types = [fuel_type.name for fuel_type in FuelType]
    print(transmission)
    print(fuel)
    print(body)
    print(year)
    
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
    
    #try converting year to int will fail if its not an int
    try:
        #try converting year to int, if it's a non-integer string it fails
        year = int(year)
    except ValueError:
        error_msg = "Year must be an integer value"
        #render add page with the error
        return error_msg, is_valid



    #checking that none of the values are 'None'
    if not make or not model or not price or not mileage or not transmission or not fuel or not body or not year:
        error_msg = "You cannot submit a form with empty fields, please try again"
        return error_msg, is_valid
    elif make == "" or make.isspace() == True:
        error_msg="Make cannot be empty or contain whitespace"
        return error_msg, is_valid
    #the dropdown options should prevent the need for this but just in case
    elif fuel not in fuel_types:
        error_msg="Declared fuel type is invalid"
    elif body not in body_types:
        error_msg="Declared body type is invalid"
    elif transmission not in transmissions:
        error_msg="Declared transmission is invalid"
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
    elif year <=0:
        error_msg = 'Year must be an integer value greater than 0'
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
                car_entry = CarListing(make=car["Make"].capitalize(), model=car["Model"], price=car["Price"], mileage=car["Mileage"],transmission=car["Transmission"], fuel=car["Fuel"], body=car["Body"], year=car["Year"], user_id = 0)
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
        user_inp = request.form.get('username').lower()
        pass_inp = request.form.get('password')
        if user_inp == "" or user_inp.isspace() ==True:
            error_msg = "Username cannot be empty or contain whitespace"
        elif pass_inp  == "" or pass_inp.isspace() ==True:
            error_msg = "Password cannot be empty or contain whitespace"
        elif user is None or user.check_password(request.form.get('password')) == False:
            error_msg=("Your login was unsuccessful, please try again")

        else:
            print("LOGIN SUCCESSFUL")
            
            flask_login.login_user(user)
            flash(f'Login successful welcome: {flask_login.current_user.username.capitalize()}!', 'success')
            return redirect(url_for("profile"))
        return render_template("login.html", error = error_msg, page_name = "login")
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
        user_inp = request.form.get("username")
        print(user_inp)
        user_inp = user_inp.lower() #normalise all usernames to lowercase
        password_inp = request.form.get("password")
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
                error = "A user with this username already exists, please try another username"
            
        return render_template('signup.html', error=error, page_name="signup")

    return render_template('signup.html', page_name = "signup")


@app.route('/user/<username>')
def show_user_profile(username):
    return f'User {escape(username)}'

@app.route('/health')
def health():
    return 'OK'

@app.route('/cars/edit/<int:car_id>', methods=['POST','GET'])
@flask_login.login_required
def edit_car(car_id):
    fuel_options = [f.name for f in FuelType]
    body_options = [b.name for b in BodyType]
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
            new_transmission = request.form.get("transmission")
            print(new_transmission)
            new_body = request.form.get("body")
            new_fuel = request.form.get("fuel")
            new_year = request.form.get("Year")
            print(new_body)
            print(new_make, new_model, new_price, new_mileage)
            error_msg, is_valid = valid_car(new_make, new_model, new_price, new_mileage, new_transmission, new_fuel, new_body, new_year)
            if is_valid:
                #if the car passes validation update the listing
                old_car_entry.make = new_make.capitalize()
                old_car_entry.model = new_model
                old_car_entry.price = new_price
                old_car_entry.mileage = new_mileage
                old_car_entry.transmission = new_transmission
                old_car_entry.fuel = new_fuel
                old_car_entry.body = new_body
                old_car_entry.year = new_year


                db.session.commit()
                flash(f'Vehicle with ID: {car_id} was successfully edited', 'success') #flashing a message for when the user is redirected
                return redirect(url_for("show_cars"))
            else:
                #if not valid return the page with the error message
                return render_template('edit.html', error=error_msg, id=car_id, car=old_car_entry, fuel_options = fuel_options, body_options = body_options)
    else:
        flash('UNAUTHORISED YOU CANNOT EDIT THIS LISTING', 'danger')
        return redirect(url_for('show_cars'))
        #rendered on the GET request
    print(fuel_options)
    return render_template('edit.html', id = car_id, car=old_car_entry, page_name = "cars", fuel_options = fuel_options, body_options = body_options)
#route for deleting cars using variable route
@app.route('/cars/delete/<int:car_id>', methods=['POST','GET'])
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
    
# @app.route('/search')
# def search_cars():
#     print("URL REACHED")
#     #request.args.get to get, the GET data
#     q=request.args.get('search_query')
#     query_search = CarListing.query.filter(CarListing.make.like(q))
#     print(query_search)
#     return render_template('cars.html', searched_cars = query_search)

@app.route('/cars')
def show_cars():
    filter_selected=False
    action_tab = False
    query_search = CarListing.query.filter_by()
    #using first() instead of one_or_none because first doesn't raise an exception when multiple rows exist

    car_makes = db.session.query(CarListing.make).distinct()
    fuel_options = [f.name for f in FuelType]
    body_options = [b.name for b in BodyType]

    if flask_login.current_user.is_authenticated and CarListing.query.filter_by(user_id = flask_login.current_user.id).first() != None:
        action_tab = True
    q=request.args.get('search_query')
    make_filter=request.args.get('make_filter')
    body_filter = request.args.get('body_filter')
    fuel_filter= request.args.get('fuel_filter')
    transmission_filter = request.args.get('transmission_filter')
    if q == None and make_filter == None:
        #display all listings if no filters or search query fetched
        cars_db = CarListing.query.all()
        return render_template('cars.html', car_list = cars_db, action_tab = action_tab, page_name = "cars", car_makes=car_makes, filter_selected=filter_selected, fuel_options = fuel_options, body_options = body_options)
    else:
        filters = {"Make": None, "Model": None, "Fuel" : None, "Body" : None, "Transmission" : None}
        print(make_filter)
        print(body_filter)
        print(fuel_filter)
        flash_str = ''
        if make_filter:
                    filters["Make"]=make_filter
                    flash_str += f'Make="{make_filter}", '
                    query_search = query_search.filter_by(make = make_filter)
                    #need to send data to the frontend (for the dependent dropdown)
                    
        if fuel_filter:                    
                    filters["Fuel"]=fuel_filter
                    flash_str += f'Fuel="{fuel_filter}", '
                    query_search = query_search.filter_by(fuel = fuel_filter)
        if body_filter:                    
                    filters["Body"]=body_filter
                    flash_str += f'Body="{body_filter}", '
                    query_search = query_search.filter_by(body = body_filter)
        if transmission_filter:                    
                    filters["Transmission"]=transmission_filter
                    flash_str += f'Transmission="{transmission_filter}", '
                    query_search = query_search.filter_by(transmission = transmission_filter)
        if q:
                print("SEARCHING FOR SOMETHING")
                #if search query is submitted 
                search = "%{}%".format(q)
                query_search = query_search.filter((CarListing.make.like(search)) | (CarListing.model.like(search) ))
                print(query_search.first())
                if query_search.first() != None:
                    if flash_str:
                        flash(f'Search Results for "{q}" {flash_str}', 'info' )
                    flash(f'Search Results for "{q}"', 'info' )
                    cars_db = query_search
                    return render_template('cars.html', car_list = cars_db, action_tab = action_tab, page_name = "cars", car_makes=car_makes, filter_selected=filter_selected, fuel_options = fuel_options, body_options = body_options)
                else:
                    if make_filter:
                        error =f'No Results found for "{q}" with filter "{filters}"'
                    else:
                        error =f'No Results found for "{q}"'
                    return render_template('cars.html', page_name = "cars", error = error, car_makes=car_makes, fuel_options = fuel_options, body_options = body_options)
        if query_search.first():
            print("AT LEAST ONE RESULT EXISTS")
            print(query_search)            
            if flash_str:
                flash(flash_str, 'info')
                cars_db = query_search
                return render_template('cars.html', car_list = cars_db, action_tab = action_tab, page_name = "cars", car_makes=car_makes, filter_selected=filter_selected, fuel_options = fuel_options, body_options = body_options)
            
        else:
            print("NO RESULTS EXIST FOR THE GIVEN FILTERS ")
            error =f'No Results found for: {flash_str}'
            return render_template('cars.html', page_name = "cars", error = error, car_makes=car_makes, fuel_options = fuel_options, body_options = body_options)
        
        if flash_str ==True:
            flash(flash_str, 'info')
        cars_db = query_search
        return render_template('cars.html', car_list = cars_db, action_tab = action_tab, page_name = "cars", car_makes=car_makes, filter_selected=filter_selected, fuel_options = fuel_options, body_options = body_options)

@app.route('/add', methods=['POST','GET'])
def add_cars():
    fuel_options = [f.name for f in FuelType]
    body_options = [b.name for b in BodyType]
    if flask_login.current_user.is_authenticated:
        if request.method == "POST":
            #if user has submitted a form extract data from it
            #strip() to clean up user input before adding to the system
            owner = flask_login.current_user.id
            make = request.form.get("Make").strip()
            model = request.form.get("Model").strip()
            price = request.form.get("Price").strip()
            mileage = request.form.get("Mileage").strip()
            transmission = request.form.get("transmission")
            fuel = request.form.get("fuel")
            body = request.form.get("body") 
            year = request.form.get("Year").strip()
            error_msg, is_valid = valid_car(make, model, price, mileage, transmission, fuel, body, year)
            if is_valid:
                #if car is valid it can be added to the database
                car_db_entry = CarListing(make=make.capitalize(), model=model, price=price, mileage=mileage, transmission=transmission, fuel=fuel, body=body, year=year, user_id = owner)
                with app.app_context():
                        db.session.add(car_db_entry)
                        db.session.commit()
                flash('Vehicle successfully added', 'success') #flashing a message for when the user is redirected
                return redirect(url_for("show_cars"))
            else:
                return render_template('add.html', error=error_msg, fuel_options= fuel_options, body_options = body_options)
    else:
        flash('You must login or sign up to sell cars', 'danger')
        return redirect(url_for("login"))
    #when user clicks on the route ('GET') render the add page
    return render_template('add.html', page_name = "add", fuel_options= fuel_options, body_options = body_options)



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

with app.test_request_context():
    print(url_for('cars'))
#     print(url_for('login'))
#     print(url_for('login', next='/'))
#     print(url_for('show_user_profile', username = 'John Doe'))
