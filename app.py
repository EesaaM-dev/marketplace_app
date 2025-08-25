from flask import Flask
from flask import Flask, flash, redirect, render_template, \
     request, url_for
from markupsafe import escape   
app = Flask(__name__)
app.secret_key = '@?nGUAl$K6_$V+%S'
cars = [{"Make" : "Mazda", "Model" : "Mazda2", "Price" : 2495, "Mileage": 87434},
        {"Make" : "Honda", "Model" : "Jazz", "Price" : 3795, "Mileage": 99873},
        {"Make" : "Toyota", "Model" : "Corolla", "Price" : 2200, "Mileage": 102224},
        {"Make" : "Suzuki", "Model" : "Swift", "Price" : 2250, "Mileage": 113000}]
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
    return render_template('cars.html', car_list = cars)

@app.route('/add', methods=['POST','GET'])
def add_cars():
    error = None
    if request.method == "POST":
        make = request.form.get("Make")
        model = request.form.get("Model")
        price = request.form.get("Price")
        mileage = request.form.get("Mileage")
        try:
            price = int(price)
        except ValueError:
            error = "Price must be an integer value"
            return render_template('add.html', error=error)
        try:
            mileage = int(mileage)
        except ValueError:
            error = "Mileage must be an integer value"
            return render_template('add.html', error=error)
        if make == None or model == None or price == None or mileage ==None:
            error = 'Values cannot be None'
            print(error)
        elif make == "" or make.isspace() == True:
            error="Make cannot be empty"
        elif model == "" or model.isspace() == True:
            error="Model cannot be empty"
        elif price <=0:
            error= 'Price must be an integer value greater than 0'
            print(error)
        elif mileage <=0:
            error = 'Mileage must be an integer value greater than 0'
            print(error)
        
        else:
            cars.append({"Make" : make, 
                        "Model" : model,
                        "Price" : price, 
                        "Mileage" : mileage})
            flash('Vehicle successfully added')
            return redirect(url_for("show_cars"))
        return render_template('add.html', error=error)
    return render_template('add.html')

if __name__ ==("__main__"):
    app.run()

# with app.test_request_context():
#     print(url_for('index'))
#     print(url_for('login'))
#     print(url_for('login', next='/'))
#     print(url_for('show_user_profile', username = 'John Doe'))



