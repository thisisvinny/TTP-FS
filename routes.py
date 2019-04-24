from flask import Flask, render_template, request, session, url_for, redirect
from werkzeug import generate_password_hash, check_password_hash
import csv

app = Flask(__name__)

@app.route("/")
def home():
	return render_template("base.html")

@app.route("/register/", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		createUser(request.form["name"], request.form["email"], request.form["password"])
		return redirect(url_for("home"))
	return render_template("register.html")

@app.route("/login/", methods=["GET", "POST"])
def login():
	if request.method == "POST":
		print(request.form)
		return render_template("login.html")
	return render_template("login.html")

def createUser(name, email, password):
	#Make sure the entered email is unique
	with open("users.csv", "r", newline="") as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row["email"] == email:
				print("Email has already been registered")
	#Create user with the given information
	with open("users.csv", "a", newline="") as csvfile:
		fieldnames = ["name", "email", "password"]
		writer = csv.DictWriter(csvfile, fieldnames)
		writer.writerow({"name": name, "email": email, "password": password})
