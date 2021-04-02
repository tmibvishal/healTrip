from flask import Flask, redirect, url_for, render_template, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
from flask import Flask, redirect, url_for, render_template, request, json
import db
import auth_queries as auth
import profile_queries as prof
import home_page_queries
import booking_queries as book

app = Flask(__name__, static_url_path='/FRONT_END/src', static_folder='FRONT_END/src', template_folder='FRONT_END')
app.config['SECRET_KEY'] = 'we are the champions'

# Setting up auth
login_manager = LoginManager()
login_manager.init_app(app)

initialise_autocomplete = False

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
	return render_template('front_page.html')

def is_valid_travel_object(travelObject):
	if isinstance(travelObject, dict):
		if "sourceCity" in travelObject and isinstance(travelObject["sourceCity"], str):
			# TODO: make departure date as date
			if "departureDate" in travelObject and isinstance(travelObject["departureDate"], str):
				if "roundTrip" in travelObject and isinstance(travelObject["roundTrip"], bool):
					if "chooseBestOrdering" in travelObject and isinstance(travelObject["chooseBestOrdering"], bool):
						if "citiesToVisit" in travelObject and isinstance(travelObject["citiesToVisit"], list) and len(travelObject["citiesToVisit"]) > 0:
							for obj in travelObject["citiesToVisit"]:
								if (isinstance(obj, dict)):
									if "cityName" in obj and isinstance(obj["cityName"], str):
										if "stayPeriod" in obj and isinstance(obj["stayPeriod"], int):
											return True
	return False

def handle_request(travelObj):
	#if is_valid_travel_object(travelObj):
	if travelObj["chooseBestOrdering"]:
		if travelObj["roundTrip"]:
			return home_page_queries.trip_best_ordering(travelObj,True)
		else:
			return home_page_queries.trip_best_ordering(travelObj,False)
		
	else:
		if travelObj["roundTrip"]:
			return home_page_queries.trip_simple(travelObj,True)
		else:
			return home_page_queries.trip_simple(travelObj,False)

	"""
	else:
		print("not valid")
		return None
	"""

@app.route("/order_cities", methods=["GET", "POST"])
def order_cities():
	if request.method == "POST":
		t = request.form.get('json')
		travelObj = json.loads(t)
		if is_valid_travel_object(travelObj):
			return render_template("order_cities.html", travelObj=travelObj)
		else:
			return render_template("order_cities.html", travelObj=None)
	return render_template("order_cities.html", travelObj=None)

def get_entries(travelObj, selections):
	entries = []
	k = 0
	for i in range(len(travelObj['flight_paths'])):
		options = travelObj['flight_paths'][i]
		#print(options)
		if len(options) == 0:
			k += 1
			entries.append({
				'entry_num': k,
				'is_hotel':False,
				'is_empty':True,
			})

		else:
			flight_ids = options[selections[k]]
			k += 1
			flights = []
			for flight_id in flight_ids:
				flight = prof.get_flight(flight_id)
				origin_airport = prof.get_airport_data(flight[3])[0]
				dest_airport = prof.get_airport_data(flight[4])[0]
				flights.append({
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
			entries.append({
				'entry_num': k,
				'is_hotel':False,
				'flights':flights,
				'is_empty':False,
			})

		if i==len(travelObj['hotels']):
			break 

		options = travelObj['hotels'][i]

		if len(options) == 0:
			k += 1
			entries.append({
				'entry_num': k,
				'is_hotel':True,
				'is_empty':True,
			})

		else:
			hotel_id = options[selections[k]]
			k += 1
			hotel = prof.get_hotel(hotel_id)
			entries.append({
				'entry_num': k,
				'is_hotel': True,
				'hotel_name':hotel[3],
				'hotel_city':hotel[1],
				'stay_period': travelObj['citiesToVisit'][i]['stayPeriod'],
				'is_empty': False,
			})
	return entries


@app.route("/output_page", methods=["POST"])
def output_page():
	t = request.form.get('json')
	travelObj = json.loads(t)
	
	if not 'selections' in travelObj:
		travelObj = handle_request(travelObj)
		print(travelObj)

	if not travelObj:
		return render_template('output_page.html', plan_found=False)
	
	if not 'selections' in travelObj:
		selections = [0 for i in range(len(travelObj['flight_paths']) + len(travelObj['hotels']))]
		travelObj['selections'] = selections

	entries = get_entries(travelObj, travelObj['selections'])
	
	return render_template("output_page.html", plan_found=True, travelObj=travelObj, entries=entries)

@app.route('/view_options', methods=['POST'])
def view_options():
	t = request.form.get('travelObj')
	entry_num = int(request.form.get('entry_num'))
	if (not t) or (not entry_num):
		render_template('404.html')
	
	travelObj = json.loads(t)
	print(travelObj)
	print(travelObj['flight_paths'])

	entries = []

	if entry_num % 2 == 1: # flight
		options = travelObj['flight_paths'][entry_num//2]
		for i, flight_ids in enumerate(options):
			flights = []
			for flight_id in flight_ids:
				flight = prof.get_flight(flight_id)
				origin_airport = prof.get_airport_data(flight[3])[0]
				dest_airport = prof.get_airport_data(flight[4])[0]
				flights.append({
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
			entries.append({
				'option_no': i,
				'is_hotel':False,
				'flights':flights,
			})
	else: # hotel
		options = travelObj['hotels'][entry_num//2 -1]
		for i, hotel_id in enumerate(options):
			hotel = prof.get_hotel(hotel_id)
			entries.append({
				'option_no': i,
				'is_hotel': True,
				'hotel_id':hotel_id,
				'hotel_name':hotel[3],
				'hotel_city':hotel[1],
				'stay_period': travelObj['citiesToVisit'][entry_num//2 - 1]['stayPeriod']
			})

	travelObj['entry_num'] = entry_num
	travelObj['num_options'] = len(entries)
	return render_template('view_options.html', travelObj=travelObj, entries=entries)



@app.route("/home")
def home():
	return render_template("home.html")

@app.route("/get_covid_status", methods=["POST"])
def get_covid_status():
	# if request.method == "POST":
	t = request.json
	cityName = t["cityName"]
	statusDict = home_page_queries.get_covid_status(cityName)
	return statusDict

@app.route("/city_name_suggestions", methods=["POST"])
def city_name_suggestions():
	# if request.method == "POST":
	t = request.json
	start_string_of_city = t["input_val"]
	cities = home_page_queries.get_all_cities(start_string_of_city)
	return {"arr": cities}

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

@app.route('/delete_user')
@login_required
def delete_user():
	id = current_user.id
	logout_user()
	auth.delete_user(id)
	flash('User deleted')
	return redirect(url_for('login'))

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
			entries.append({
				'is_hotel':True,
				'hotel_name':hotel[3],
				'hotel_city':hotel[1],
				'stay_period':booking_entry[4]
			})
		else:
			flight = prof.get_flight(booking_entry[3])
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

@app.route('/hotel/<hotel_id>', methods=['GET','POST'])
def hotel_page(hotel_id):
	hotel = prof.get_hotel(hotel_id)
	if not hotel:
		return render_template('404.html')
	
	reviews = prof.get_reviews(hotel_id)
	
	sum_ratings, num_ratings = 0, 0
	for review in reviews:
		num_ratings += 1
		sum_ratings += int(review[3])
	avg_rating = -1
	if num_ratings > 0:
		avg_rating = sum_ratings / num_ratings
		avg_rating = "{:.2f}".format(avg_rating)

	hotel_state = prof.get_state(hotel[2])
	if not hotel_state:
		return render_template('404.html')

	if request.method=='POST':
		t = request.form.get('json')
		travelObj = json.loads(t)
		return render_template('hotel.html', preview=True, travelObj=travelObj, hotel=hotel, reviews=reviews, avg_rating=avg_rating, hotel_state=hotel_state)

	return render_template('hotel.html', preview=False, hotel=hotel, reviews=reviews, avg_rating=avg_rating, hotel_state=hotel_state)

@app.route('/book_trip', methods=['POST'])
@login_required
def book_trip():
	t = request.form.get('json')
	travelObj = json.loads(t)

	selections = travelObj['selections']
	first_flight_id = travelObj['flight_paths'][0][selections[0]][0]

	first_flight = prof.get_flight(first_flight_id)
	
	source_airport_code = first_flight[3]
	user_id = current_user.id
	departure_date = travelObj['departureDate']

	book.add_booking(source_airport_code, user_id, departure_date)
	booking_id = book.get_last_booking_id(user_id)

	hotel_i, flight_i = 0, 0
	for k in range(len(selections)):
		if k % 2 == 0: # flight
			flight_ids = travelObj['flight_paths'][flight_i][selections[k]]
			for flight_id in flight_ids:
				book.add_flight_entry(booking_id, flight_id)
			flight_i += 1
		else:
			hotel_id = travelObj['hotels'][hotel_i][selections[k]]
			stay_period = travelObj['citiesToVisit'][hotel_i]['stayPeriod']
			book.add_hotel_entry(booking_id, hotel_id, stay_period)
			hotel_i += 1

	return redirect(url_for('profile'))


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
