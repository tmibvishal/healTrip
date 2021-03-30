from datetime import date, datetime
from flask import Flask, redirect, url_for, render_template, request, json
import db

app = Flask(__name__, static_url_path='/FRONT_END/src', static_folder='FRONT_END/src', template_folder='FRONT_END')

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
