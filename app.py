from flask import Flask
from flask import Flask, flash, redirect, render_template, \
     request, url_for
from markupsafe import escape   
from flask_sqlalchemy import SQLAlchemy





app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///car_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class CarListing(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    make = db.Column(db.String(30), nullable = False)
    model = db.Column(db.String(30), nullable = False)
    price = db.Column(db.Integer, nullable = False)
    mileage = db.Column(db.Integer, nullable = False)

    def __repr__(self):
        return f"ID : {self.id} Make: {self.make} Model: {self.model} Price: {self.price}  Mileage: {self.mileage}"
#need secret key for when flashing messages
app.secret_key = '@?nGUAl$K6_$V+%S' 

#list of cars which creates each row of the table 
cars = [{"Make" : "Mazda", "Model" : "Mazda2", "Price" : 2495, "Mileage": 87434},
        {"Make" : "Honda", "Model" : "Jazz", "Price" : 3795, "Mileage": 99873},
        {"Make" : "Toyota", "Model" : "Corolla", "Price" : 2200, "Mileage": 102224},
        {"Make" : "Suzuki", "Model" : "Swift", "Price" : 2250, "Mileage": 113000}]




def populate_db():
        #check if database already has data if empty populate it
        if CarListing.query.first() !=None:
            print("Car database already has data")
        else:
            for car in cars:
                car_entry = CarListing(make=car["Make"], model=car["Model"], price=car["Price"], mileage=car["Mileage"])
                with app.app_context():
                    db.session.add(car_entry)
                    db.session.commit()

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    return 'login'

# @app.route('/user/<username>')
# def show_user_profile(username):
#     return f'User {escape(username)}'

@app.route('/health')
def health():
    return 'OK'

@app.route('/edit', methods=['PUT','GET'])
def edit_cars():
    return render_template('edit.html')
#route for deleting cars using variable route
@app.route('/delete/<car_id>', methods=['POST','GET'])
def delete_car(car_id):

    #implement logic for deleting from the database where car.id is car_id
    car_entry = CarListing.query.get(car_id)
    #db.session.delete(car_entry)
    #db.session.commit()
    print(car_entry)
    flash(f'Vehicle with ID: {car_id} successfully Deleted') #flashing a message for when the user is redirected
    return redirect(url_for("show_cars"))

@app.route('/cars')
def show_cars():
    cars_db = CarListing.query.all()
    return render_template('cars.html', car_list = cars_db)

@app.route('/add', methods=['POST','GET'])
def add_cars():
    error = None
    if request.method == "POST":
        #if user has submitted a form extract data from it
        make = request.form.get("Make")
        model = request.form.get("Model")
        price = request.form.get("Price")
        mileage = request.form.get("Mileage")
        try:
            #try converting price to int if it's a non-integer string it will fail
            price = int(price)
        except ValueError:
            error = "Price must be an integer value"
            #render the add page again with the error
            return render_template('add.html', error=error) 
        try:
            #try converting mileage to int, if it's a non-integer string it fails
            mileage = int(mileage)
        except ValueError:
            error = "Mileage must be an integer value"
            #render add page with the error
            return render_template('add.html', error=error)
        #checking that none of the values are 'None'
        if make == None or model == None or price == None or mileage ==None:
            error = 'Values cannot be None'
            print(error)
            #check if make is empty or if it is comprised of just whitespace
        elif make == "" or make.isspace() == True:
            error="Make cannot be empty"
        elif model == "" or model.isspace() == True:
            error="Model cannot be empty"
            #checking that price is a positive integer
        elif price <=0:
            error= 'Price must be an integer value greater than 0'
            print(error)
        elif mileage <=0:
            error = 'Mileage must be an integer value greater than 0'
            print(error)
        else:
            #if input validation is successful append to the cars list
            # cars.append({"Make" : make, 
            #             "Model" : model,
            #             "Price" : price, 
            #             "Mileage" : mileage})
            
            car_db_entry = CarListing(make=make, model=model, price=price, mileage=mileage)
            with app.app_context():
                    db.session.add(car_db_entry)
                    db.session.commit()
            flash('Vehicle successfully added') #flashing a message for when the user is redirected
            return redirect(url_for("show_cars"))
        #if input validation fails re-render the add.html page along with the error
        return render_template('add.html', error=error)
    return render_template('add.html') #when user clicks on the route ('GET') render the add page
if __name__ ==("__main__"):
    #database is only created if a database doesn't already exist
    #this also prevents my fake data from being duplicated in the database
    with app.app_context():
        db.create_all() #create the database and tables
        populate_db()
    print("app running now ")
    app.run(debug=True)    

# with app.test_request_context():
#     print(url_for('index'))
#     print(url_for('login'))
#     print(url_for('login', next='/'))
#     print(url_for('show_user_profile', username = 'John Doe'))
