from flask import Flask, redirect, url_for, render_template, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
from flask import Flask, redirect, url_for, render_template, request, json
import db
import auth_queries as auth
import profile_queries as prof

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

@app.route("/profile")
@login_required
def profile():
	user = auth.get_user_from_userid(current_user.id)
	user_bookings = prof.get_user_bookings(current_user.id)
	num_bookings = 0
	bookings_data = []
	for booking in user_bookings:
		num_bookings += 1
		src_airport = prof.get_airport_data(booking[2])[0]
		dep_date = str(booking[3])
		num_flights = prof.get_num_flights(booking[0])
		num_hotels = prof.get_num_hotels(booking[0])
		print(num_flights, num_hotels)
		bookings_data.append({
			'id':booking[0],
			'src_airport':src_airport,
			'dep_date':dep_date,
			'num_hotels':num_hotels,
			'num_flights':num_flights
		})	
	return render_template('profile.html', user_uname=user[1],user_email=user[2], num_bookings=num_bookings, bookings = bookings_data)

@app.route('/edit_profile')
@login_required
def edit_profile():
	user = auth.get_user_from_userid(current_user.id)
	return render_template('edit_profile.html', uname=user[1], email=user[2])

@app.route('/edit_profile', methods=['POST'])
@login_required
def edit_profile_post():
	uname = request.form.get('uname')
	email = request.form.get('email')

	user = auth.get_user_from_uname(uname)
	if user and user[0] != current_user.id:
		flash('Username already taken')
		return redirect(url_for('edit_profile'))
	user = auth.get_user_from_email(email)
	if user and user[0] != current_user.id:
		flash('Another account with this email already exists')
		return redirect(url_for('edit_profile'))
	
	auth.update_user_details(current_user.id, uname, email)
	flash('Details updated')
	return redirect(url_for('profile'))

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
	old_password = request.form.get('old_password')
	new_password = request.form.get('new_password')

	user = auth.get_user_from_userid(current_user.id)
	if not check_password_hash(user[3], old_password):
		flash('Old password is incorrect')
		return redirect(url_for('edit_profile'))
	if len(new_password)==0:
		flash('Password cannot be empty')
		return redirect(url_for('edit_profile'))
	
	auth.update_password(current_user.id, generate_password_hash(new_password))
	flash('Password updated')
	return redirect(url_for('profile')) 


@app.route('/booking_details/<booking_id>')
@login_required
def booking_details(booking_id):
	booking = prof.get_booking(booking_id)
	if len(booking)==0:
		return render_template('404.html')
	booking = booking[0]
	dep_date = str(booking[3])
	if booking[1] != current_user.id:
		return render_template('invalid_access.html')
	booking_entries = prof.get_booking_entries(booking_id)
	entries = []
	for booking_entry in booking_entries:
		if(booking_entry[2]): # hotel
			hotel = prof.get_hotel(booking_entry[3])
			hotel = hotel[0]
			entries.append({
				'is_hotel':True,
				'hotel_name':hotel[3],
				'hotel_city':hotel[1],
				'stay_period':booking_entry[4]
			})
		else:
			flight = prof.get_flight(booking_entry[3])[0]
			origin_airport = prof.get_airport_data(flight[3])[0]
			dest_airport = prof.get_airport_data(flight[4])[0]
			entries.append({
				'is_hotel':False,
				'origin_code':origin_airport[2],
				'origin_city':origin_airport[0],
				'dest_code':dest_airport[2],
				'dest_city':dest_airport[0],
				'dep_time':str(flight[5])[:-2] + ':' + str(flight[5])[-2:],
				'arr_time':str(flight[6])[:-2] + ':' + str(flight[6])[-2:],
				'date':str(flight[1]),
				'carrier':flight[2]
			})
	return render_template('booking_details.html', entries=entries, dep_date=dep_date)

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
