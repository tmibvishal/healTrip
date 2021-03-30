from flask import Flask, redirect, url_for, render_template, request
import db

app = Flask(__name__, static_url_path='/FRONT_END/src', static_folder='FRONT_END/src', template_folder='FRONT_END')

@app.route("/")
def index():
	return render_template("index.html")

@app.route("/order_cities")
def order_cities():
	return render_template("order_cities.html")

@app.route("/<name>")
def user(name):
	return f"Hello! This is <b>{name}</b>."

@app.route("/admin")
def admin():
	return redirect(url_for("user", name="Vishal Singh (Admin)"))

@app.route("/login")
def login():
	return render_template('login.html')

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
