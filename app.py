from flask import Flask, redirect, url_for, render_template

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

if __name__ == "__main__":
	app.run(debug=True, port=5022)
