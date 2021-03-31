from flask import Flask, redirect, url_for, render_template, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
from flask import Flask, redirect, url_for, render_template, request, json
import db
import auth_queries as auth

app = Flask(__name__, static_url_path='/FRONT_END/src', static_folder='FRONT_END/src', template_folder='FRONT_END')
app.config['SECRET_KEY'] = 'we are the champions'

# Setting up auth
login_manager = LoginManager()
login_manager.init_app(app)

class User:
	def __init__(self, user):
		self.id = user[0]

	def is_authenticated(self):
		return True
	
	def is_active(self):
		return True

	def is_anonymous(self):
		return False
	
	def get_id(self):
		return self.id

@login_manager.user_loader
def load_user(user_id):
	user = auth.get_user_from_userid(user_id)
	if not user:
		return None
	return User(user)

@app.route("/login")
def login(name=''):
	return render_template('login.html', name=name)

@app.route("/login", methods=['POST'])
def login_post():
	name = request.form.get('name')
	password = request.form.get('password')
	remember = request.form.get('remember')
	user = None
	if '@' in name:
		user = auth.get_user_from_email(name)
	else:
		user = auth.get_user_from_uname(name)

	if user is None:
		flash('Account not found. Please register first.')
		return redirect(url_for('login', name=name))

	if not check_password_hash(user[3], password):
		flash('Incorrect password.')
		return redirect(url_for('login', name=name))

	user_obj = User(user)
	login_user(user_obj, remember=remember)
	return redirect(url_for('profile'))

@app.route("/register")
def register(username='', email=''):
	return render_template('register.html', username=username, email=email)

@app.route("/register", methods=['POST'])
def register_post():
	username = request.form.get('username')
	email = request.form.get('email')
	password = request.form.get('password')
	
	user = auth.get_user_from_uname(username)
	if user:
		flash('An account with given username already exists. Please pick a new username')
		return redirect(url_for('register'))

	user = auth.get_user_from_email(email)
	if user:
		flash('An account with given email already exists. Consider logging in.')
		return redirect(url_for('register'))

	hashed_password = generate_password_hash(password, method='sha256')
	
	auth.new_user(username, email, hashed_password)

	user = auth.get_user_from_uname(username)
	user_obj = User(user)
	login_user(user_obj)
	return redirect(url_for('profile'))

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))


@app.route("/")
def index():
	return render_template("index.html")

@app.route("/order_cities")
def order_cities():
	travelObj = {"sourceCity": "Seattle", "departureDate": date.today()}
	return render_template("order_cities.html", travelObj=travelObj)

@app.route("/output_page", methods=["GET", "POST"])
def output_page():
	if request.method == "POST":
		print("hello")
		t = request.form.get('json')
		travelObj = json.loads(t)
		print(travelObj)
		return render_template("output_page.html", travelObj=travelObj)
	travelObj = {"sourceCity": "YoYo", "departureDate": date.today()}
	return render_template("output_page.html", travelObj=travelObj)

def process_data(travelObj):
	# TODO: try to take input of gap time
	query = """
	WITH RECURSIVE all_paths(originairportid, destairportid, curpath, arr_date, arr_time) AS (
		SELECT originairportid, destairportid, ARRAY[originairportid, destairportid], (CASE WHEN (crs_dep_time<crs_arr_time) THEN fl_date ELSE  (fl_date+INTERVAL '1 day')), crs_arr_time FROM (flights F JOIN airport_codes AC ON (F.origin=AC.airport_code AND city="Chicago"))
		UNION
		SELECT all_paths.originairportid, flights.destairportid, array_append(curpath, flights.destairportid), (CASE WHEN (crs_dep_time<crs_arr_time) THEN fl_date ELSE  (fl_date+INTERVAL '1 day')), crs_arr_time FROM all_paths, flights WHERE (all_paths.destairportid=flights.originairportid AND NOT (flights.destairportid = ANY(curpath)) AND (crs_dep_time<crs_arr_time OR arr_date<fl_date))
	)
	SELECT originairportid, destairportid, arr_date, arr_time AS length FROM (
		all_paths AP JOIN airport_codes AC ON (AC.airport_code=AP.destairportid AND AC.city="Dallas")
	) ORDER BY arr_date DESC, arr_time DESC LIMIT 1;
	"""

@app.route("/home")
def home():
	return render_template("home.html")

@app.route("/profile")
@login_required
def profile():
	user = auth.get_user_from_userid(current_user.id)
	user_bookings = auth.get_user_bookings(current_user.id)
	num_bookings = 0
	for booking in user_bookings:
		num_bookings += 1	
	return render_template('profile.html', user_uname=user[1],user_email=user[2], num_bookings=num_bookings)

@app.route("/<name>")
def user(name):
	return f"Hello! This is <b>{name}</b>."

@app.route("/admin")
def admin():
	return redirect(url_for("user", name="Vishal Singh (Admin)"))

# example of database
@app.route('/toys', methods=["GET", "POST"])
def toys():
    if request.method == "POST":
        db.add_toy(request.form['name'])
        return redirect(url_for('index'))
    return render_template('dbexample.html', toys=db.get_all_toys())

if __name__ == "__main__":
	
	# if not first time then remove this
	app.run(debug=True, port=5022)
