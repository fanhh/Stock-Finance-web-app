import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    current_user = session["user_id"]
    cash = db.execute("SELECT cash FROM users Where id = ?", current_user)
    transaction= db.execute("SELECT stock, shares from transactions WHERE user_id = ?", current_user)
    total = 0
    for transactions in transaction:
        p = lookup(transactions["stock"])
        total += (p["price"] * transactions["shares"])

    try:

        return render_template("index.html", money = cash[0]["cash"], transaction = transaction, lookup = lookup, usd = usd, round = round, t = total)
    except IndexError:
        return redirect("/")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")

    else:
        # Extract the data from the sumbit form
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        check = lookup(symbol)

        # If the input is blank or don't exist
        if symbol == "" or check == None:
            return apology("Input is Blank or Symbol don't exist")


        # Check if it's number
        try:
            shares = int(shares)
        except ValueError:
            return apology("Must be a real number")

        # If the share is a negative interger
        if shares < 0:
            return apology("Can't be a negitive number")

        # Set the value for the current user
        current_user = session["user_id"]

        # Check the user current cash value
        cashes = db.execute("SELECT cash FROM users WHERE id = ?", current_user)
        cashes = float(cashes[0]["cash"])

        # Check whether the current user have enough money
        difference = float(cashes - (check["price"] * shares))
        if difference <= 0:
            return apology("Not enough money")

        # Get a record of the current stock the users own
        record = db.execute("SELECT stock from transactions WHERE User_id = ?", current_user)

        # If the users owns the stock he is purchasing
        if symbol.upper() in [x["stock"] for x in record]:
            current_shares = db.execute("SELECT shares FROM transactions WHERE User_id = ? AND stock = ?", current_user, symbol.upper())
            total = int(current_shares[0]["shares"]) + shares
            db.execute("UPDATE transactions SET shares = ? WHERE stock = ? AND User_id = ?", round(total, 2), symbol.upper(), current_user)


        else:
            db.execute("INSERT INTO transactions(User_id, stock, shares) VALUES(?,?,?)", current_user, symbol.upper(),shares)


        db.execute("INSERT INTO history(user_id, stock, shares, balance, date) VALUES(?,?,?,?,CURRENT_TIMESTAMP)", current_user, symbol.upper(), shares, round(difference, 2))

        db.execute("UPDATE users SET cash = ? WHERE id = ?", difference, current_user)
        return redirect("/")





@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    current_user = session["user_id"]
    history = db.execute("SELECT * FROM history WHERE user_id = ?", current_user)
    return render_template("history.html", history = history, round = round)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    else:
        # Get the input value from the input
        symbolp = request.form.get("symbol")

        # Look up the input symbol
        check = lookup(symbolp)

        # Check if the symbol exist
        if check == None:
            return apology("Symbol does not exist")
        else:
            # Pass in the dictonaries values into the html
            return render_template("quoted.html", name=check["name"], price=check["price"], symbol=check["symbol"], usd = usd)




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "GET":
        return render_template("register.html")
    else:
        # Extract the input values
        username = request.form.get("username")
        passw = request.form.get("password")
        check = request.form.get("confirmation")



        # Check the if any input is blank
        if username == "" or passw == "" or check == "":
            return apology("Can't leave the input blank")

        # Check if the password matches
        elif passw != check:
            return apology("Password don't match")


        # Hash the users password
        hashp = generate_password_hash(passw, method="pbkdf2:sha256", salt_length=8)

        # Insert the users name and hash into the table
        # Check for duplicate username
        try:
            db.execute("INSERT INTO users(username, hash) VALUES(?,?)", username, hashp)
        except ValueError:
            return apology("Duplicate name")

        # Look up the user location in the database
        row = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Keep the user log in
        session["user_id"] = row[0]["id"]

        # Direct the log in user to home page
        return redirect("/")



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    user_id = session["user_id"]
    records = db.execute("SELECT stock FROM transactions WHERE user_id = ?", user_id)


    if request.method == "GET":
        return render_template("sell.html", records = records)
    else:
        # Vars for all the inputs in the html formats
        current_user = session["user_id"]

        symbol = request.form.get("symbol")

        shares = request.form.get("shares")


        # Check to see if the users have the stock
        if str(symbol) not in [x["stock"] for x in records]:

            return apology("Symbol don't exist")


        # Check if the user input of the shares
        elif int(shares) <= 0:

            return apology("Can't sell negative shares")

        # Check the databases of the users inventory
        try:

            stock_holding = db.execute("SELECT shares FROM transactions WHERE stock = ? AND User_id = ?",
            symbol.upper(), current_user)

        except ValueError:

            return apology("You don't have this stock")


        # Check the amout of shares user want to sell
        if int(shares) > int(stock_holding[0]["shares"]):
            return apology("You do not own that many shares")


        # Look up the current price of the stocks
        price = lookup(symbol)

        # Calulate the sum of the stock cash values
        total = float(shares) * price["price"]

        # Select current cash values users have form the database
        current_cash = db.execute("SELECT cash FROM users WHERE id = ?", current_user)

        # Add it to the sum
        total += current_cash[0]["cash"]


        # Update users database
        db.execute("UPDATE users SET cash = ? WHERE id = ?", total, current_user)

        # Number shares after the sell
        new_shares = stock_holding[0]["shares"] - int(shares)

        # IF the users have zero shares
        if new_shares == 0:

            # Delete the stocks from the users profile
            db.execute("DELETE FROM transactions WHERE stock = ? AND User_id = ?",symbol.upper(), current_user)

        else:

            # Update the users stocks shares number
            db.execute("UPDATE transactions SET shares = ? WHERE User_id = ? AND stock = ?",
            new_shares, current_user, symbol.upper())


        # Update the history of this user activites
        db.execute("INSERT INTO history(user_id, stock, shares, balance, date) VALUES(?,?,?,?,CURRENT_TIMESTAMP)",
        current_user, symbol.upper(), shares, total)

        return redirect("/")


