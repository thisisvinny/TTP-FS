from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")
def home():
	return render_template("base.html")

@app.route("/register/", methods=["GET", "POST"])
def register():
	if request.method == "GET":
		return render_template("register.html")

@app.route("/login/", methods=["GET", "POST"])
def login():
	if request.method == "GET":
		return render_template("login.html")