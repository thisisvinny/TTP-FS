from flask import Flask, render_template, request, session, url_for, redirect, flash
from werkzeug import generate_password_hash, check_password_hash
import sqlite3
import requests
import json

app = Flask(__name__)
app.secret_key = "TTP-FS"

iex_api_base = "https://api.iextrading.com/1.0/stock/"
iex_api_open_price = "/ohlc"
iex_api_current_price = "/price"

@app.route("/")
def home():
	return render_template("base.html")

@app.route("/register/", methods=["GET", "POST"])
def register():
	if "email" in session:
		return redirect(url_for("home"))

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
				cur.execute("insert into users (name, email, password, balance) values (?,?,?, 5000.00)", (name, email, generate_password_hash(password)))
				con.commit()
				id_num = cur.execute("select id from users where email=?", (email, )).fetchone()[0]
		except:
			con.rollback()
		finally:
			con.close()
		session["id"] = id_num
		session["name"] = name
		session["email"] = email
		return redirect(url_for("home"))
	return render_template("register.html")

@app.route("/login/", methods=["GET", "POST"])
def login():
	if "email" in session:
		return redirect(url_for("home"))

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
						id_num, name = cur.execute("select id, name from users where email=?", (email, )).fetchone()
						session["id"] = id_num
						session["name"] = name
						session["email"] = email
						return redirect(url_for("home"))
				flash("Incorrect username or password.")
				return redirect(url_for("login"))
		except:
			con.rollback()
		finally:
			con.close()
	return render_template("login.html")

@app.route("/logout/")
def logout():
	if "email" in session:
		session.pop("id", None)
		session.pop("name", None)
		session.pop("email", None)
	return redirect(url_for("home"))


#https://api.iextrading.com/1.0/stock/aapl/price
#https://api.iextrading.com/1.0/stock/aapl/ohlc
iex_api_base = "https://api.iextrading.com/1.0/stock/"
iex_api_open_price = "/ohlc"
iex_api_current_price = "/price"

@app.route("/portfolio/", methods=["GET", "POST"])
def portfolio():
	if "email" not in session:
		return redirect(url_for("home"))

	#Post method, buy stocks
	if request.method == "POST":
		#check symbol is valid
		ticker_symbol = request.form["ticker_symbol"]
		url = iex_api_base + ticker_symbol + iex_api_current_price
		response = requests.get(url)
		if response.status_code == 404:
			flash("Invalid Ticker Symbol.")
			return redirect(url_for("portfolio"))

		#check quantity is non empty
		try:
			quantity = float(request.form["quantity"])
		except:
			flash("Enter a valid quantity.")
			return redirect(url_for("portfolio"))

		#check user has enough cash to buy the quantity specified
		price = json.loads(response.text)
		with sqlite3.connect("database.db") as con:
			cur = con.cursor()
			balance = cur.execute("select balance from users where id=?", (session["id"], )).fetchone()[0]
			spending = quantity*price
			#insufficient balance
			if balance < spending:
				flash("Insufficient balance. Attempted to spend $%.2f."%(spending))
				return redirect(url_for("portfolio"))
			#otherwise, complete the transaction, update user transactions and portfolios
			cur.execute("update users set balance=? where id=?", (balance-spending, session["id"]))
			cur.execute("insert into transactions (id, type, ticker_symbol, quantity, price) values (?,'Buy',?,?,?)", (session["id"], ticker_symbol, quantity, price))
			cur.execute("insert into portfolio (id, ticker_symbol, quantity, price) values (?,?,?,?)", (session["id"], ticker_symbol, quantity, price))
		con.close()
		return redirect(url_for("portfolio"))
	#Get method, display page with the user's stock portfolio and cash
	with sqlite3.connect("database.db") as con:
		cur = con.cursor()
		cash = "%.2f" % cur.execute("select balance from users where id=?", (session["id"], )).fetchone()[0]
	con.close()
	return render_template("portfolio.html", cash=cash)

@app.route("/transactions/")
def transactions():
	if "email" not in session:
		return redirect(url_for("home"))
	return render_template("transactions.html")