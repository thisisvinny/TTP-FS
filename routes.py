from flask import Flask, render_template, request, session, url_for, redirect, flash
from werkzeug import generate_password_hash, check_password_hash
import sqlite3

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
				if email_exists:
					flash("An account with that email already exists.")
					return redirect(url_for("register"))
				cur.execute("insert into users (name, email, password) values (?,?,?)", (name, email, generate_password_hash(password)))
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
		try:
			email = request.form["email"]
			password = request.form["password"]
			with sqlite3.connect("database.db") as con:
				cur = con.cursor()
				#check if email is associated with an account
				email_exists = cur.execute("select email from users where email=?", (email,)).fetchone()
				if email_exists:
					#verify email and password are correct
					hashed_password = cur.execute("select password from users where email=?", (email, )).fetchone()[0]
					if check_password_hash(hashed_password, password):
						return redirect(url_for("home"))
				flash("Incorrect username or password.")
				return redirect(url_for("login"))
		except:
			con.rollback()
		finally:
			con.close()
	return render_template("login.html")
