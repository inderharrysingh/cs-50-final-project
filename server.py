from functools import wraps

import flask_bootstrap as fb
from flask import Flask, render_template, request, url_for, session, redirect, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from datafetcher import datasender, idsender

app = Flask(__name__)
fb.Bootstrap(app)

data = {
    'Diet': ['Balanced', 'High-Fiber', 'High-Protein', 'Low-Carb', 'Low-Fat', 'Low-Sodium'],
    'Allergy': ['Vegetarian', 'Wheat-Free', 'Low-Sugar', 'Alcohol-Cocktail', 'Alcohol-Free', 'Celery-Free',
               'Crustcean-Free', 'Daily-Free', 'Egg-Free',
               'Fish-Free', 'FODMAP-Free', 'Gluten-Free', 'Immuno-Supportive', 'Keto-Friendly', 'Kosher'],
    'Meal Type': ['Breakfast', 'Brunch', 'Lunch', 'Dinner', 'Snack', 'Teatime'],
    'Dish Type': ['Sweets', 'Soup', 'Side Dish', 'Seafood', 'Alcohol Cocktail', 'Biscuit and Cookies', 'Bread',
                  'Cereals', 'Condiments and Sauces',
                  'Desserts', 'Drinks', 'Egg', 'Ice Cream and Custard', 'Main Course', 'Pancake', 'Pasta',
                  'Starter'],
    'Cuisine Type': ['American', 'Asian', 'British', 'Carribbean', 'Central Europe',
                     'Chinese', 'Eastern Europe', 'French', 'Greek', 'Indian', 'Italian',
                     'Japanese', 'Korean', 'Kosher', 'Mediterranean', 'Mexican', 'Middle Eastern',
                     'Nordic', 'South American', 'South East Asian']
}
response = 0

# CONFIGURING THE DATABASE
app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# CREATING THE DATABASE
with app.app_context():
    class Users(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(250))
        email = db.Column(db.String(250))
        hash = db.Column(db.String(1000))


    class Book(db.Model):
        __tablename__ = 'bookmark'
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer)
        recipe_id = db.Column(db.Integer)

# CONFIGURING THE SESSION
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


# PREREQUISITE FOR CONFIGURING THE SESSION CONTROL
@app.after_request
def after_request(response):
    response.headers['Cache-control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = 0
    response.headers['Pragma'] = 'no-cache'
    return response


# DECORATOR TO CHECK WHERTHER SOMEONE IS LOGGED IN OR NOT WITH THE HELP OF SESSION
def login_required(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect('/login')
        return f(*args, **kwargs)

    return decorator_function


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password1')
        c_password = request.form.get('password2')

        if name == '' or email == '' or password == '' or c_password == '':
            flash("Don't leave any field blank")
            return redirect('/register')

        if password != c_password:
            flash("Passwords doesn't match")
            return redirect('/register')

        with app.app_context():
            new_user = Users(name=name, email=email, hash=generate_password_hash(password, salt_length=6))
            db.session.add(new_user)
            db.session.commit()

            # ADDING TO THE SESSION
            session['user_id'] = Users.query.filter_by(name=name).first().id

            return redirect('/login')
    return render_template("register.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if email == '' or password == '':
            flash("Please don't leave any field blank ")
            return redirect('login')

        with app.app_context():
            user = Users.query.filter_by(email=email).first()
            if user == None:
                flash('This email is not registered please register first! ')
                return redirect('/register')

            if not check_password_hash(user.hash, password):
                flash('Invalid Password, Try again')
                return redirect('/login')

            session['user_id'] = user.id

        return redirect('/search')

    return render_template('login.html')


@app.route('/search', methods=['POST', "GET"])
@login_required
def search():
    if request.method == "POST":

        ingredients = request.form.get('ingredients')
        diet = request.form.get('Diet')
        cuisine = request.form.get('CuisineType')
        health = request.form.get('Health')
        dish = request.form.get('DishType')
        meal = request.form.get('MealType')

        if ingredients == '':
            flash("Can leave ingredients field empty!")
            return redirect('/search')

        if ingredients == None:
            return "ingredients field can't be empty"

        global response
        response = datasender(q=ingredients, diet=diet, cuisineType=cuisine, dishType=dish, health=health,
                              mealType=meal)

        return redirect(url_for('result'))

    return render_template('main.html', data=data)


@app.route("/result")
@login_required
def result():
    return render_template('search.html', data=response)


# working with the json post request
@app.route('/update', methods=['POST', 'GET'])
def update():
    index = int(request.form.get('id'))
    return render_template('card.html', data=response[index])


@app.route('/bookmark', methods=['GET', 'POST'])
@login_required
def bookmark():
    id = request.args.get('id')
    with app.app_context():
        new_bookmark = Book(
            user_id=int(session.get('user_id')),
            recipe_id=id
        )
        db.session.add(new_bookmark)
        db.session.commit()
    return render_template('search.html', data=response)


@app.route('/saved')
@login_required
def saved():
    with app.app_context():
        id = session.get('user_id')
        row = Book.query.filter_by(user_id=id).all()
        if row == []:
            return render_template('bookmark.html', data=[])
        if len(row) == 1:
            data = idsender(row[0].recipe_id)
            data = [data]
        else:
            data = []
            for i in row:
                value = idsender(i.recipe_id)
                data.append(value)

    return render_template('bookmark.html', data=data)


@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('/login')




@app.route('/remove')
def remove():
    with app.app_context():
        id = request.args.get('id')
        row = Book.query.filter_by(recipe_id=id).first()
        db.session.delete(row)
        db.session.commit()

    return redirect('/saved')


if __name__ == "__main__":
    app.run(debug=True)
