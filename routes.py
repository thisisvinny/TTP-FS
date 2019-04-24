from flask import Flask, render_template, request, session, url_for, redirect, flash
from werkzeug import generate_password_hash, check_password_hash
import csv

app = Flask(__name__)
app.secret_key = "TTP-FS"

@app.route("/")
def home():
	return render_template("base.html")

@app.route("/register/", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		try:
			name = request.form["name"]
			email = request.form["email"]
			password = request.form["password"]
			with sqlite3.connect("database.db") as con:
				cur = con.cursor()
				#check if email exists
				email_exists = cur.execute("select email from users where email=?", (email, )).fetchone()
				if(email_exists):
					flash("An account with that email already exists.")
					return redirect(url_for("register"))
				cur.execute("insert into users (name, email, password) values (?,?,?)", (name, email, password))
				con.commit()
		except:
			con.rollback()
		finally:
			con.close()
		return redirect(url_for("home"))
	return render_template("register.html")

@app.route("/login/", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		print(request.form)
		return render_template("login.html")
	return render_template("login.html")