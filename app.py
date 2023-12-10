import os

import sqlite3
import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import random

from helpers import apology, login_required



# Configure application
app = Flask(__name__)
app.secret_key = os.urandom(16)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def hello_world():
    """home page"""
    return redirect("/index")

if __name__ == '__main__':
    app.run(debug=True)


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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        elif not request.form.get("confirmation"):
            return apology("must provide password", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) > 0:
            return apology("Username already taken", 400)

        # Check if passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology ("passwords do not match", 400)

        username = request.form.get("username")
        pass_hash = generate_password_hash(request.form.get("password"))
        email = request.form.get("email")

        db.execute("INSERT INTO users (username, hash, email) VALUES (:username, :hash, :email)", username=username, hash=pass_hash, email=email)

        return apology ("SUCCES", 200)

    else:
        return render_template("register.html")

    ##return apology("TODO")

@app.route('/index')
@login_required
def index():
    """ history page"""
    return apology ("error index")

@app.route('/rps', methods=["GET", "POST"])
@login_required
def rps():
    """rock paper scissor"""

    player_image = None
    comp_image = None

    if request.method == "GET":
        # Initialize scores if they don't exist in session
        session['score_you'] = 0
        session['score_ai'] = 0
        return render_template("rps.html")

    if request.method == "POST":
        choice = request.form.get("choice")
        options = ["rock", "paper", "scissors"]
        comp_choice = random.choice(options)

        # Compare choices and update scores in session
        if comp_choice == choice:
            result = "tie"
        elif (choice == "rock" and comp_choice == "scissors") or \
             (choice == "scissors" and comp_choice == "paper") or \
             (choice == "paper" and comp_choice == "rock"):
            session['score_you'] += 1
            result = "win"
        else:
            session['score_ai'] += 1
            result = "lose"

        player_image = f"you_{choice}.png"
        comp_image = f"comp_{comp_choice}.png"

        return render_template("rps.html", result=result, ai=session['score_ai'], you=session['score_you'], player_image=player_image, comp_image=comp_image)


@app.route('/hl', methods=["GET", "POST"])
@login_required
def hl():
    """higher lower"""

    random_number = random.randint(1, 100)

    if request.method == "GET":
        return render_template ("hl.html", random_number = random_number)

    if request.method == "POST":
        random_number_ai = random.randint(1,100)
        choice = request.form.get("choice")

        print(random_number)
        print(random_number_ai)

        if choice == "higher":
            if random_number > random_number_ai:
                return apology ("correct")
            else:
                return apology ("incorrect")

        if choice == "tie":
            if random_number == random_number_ai:
                return apology ("correct")
            else:
                return apology ("incorrect")

        if choice == "lower":
            if random_number < random_number_ai:
                return apology ("correct")
            else:
                return apology ("incorrect")

        return apology ("post")

@app.route('/hangman', methods=["GET", "POST"])
@login_required
def hangman():
    """hangman"""

    words = ["example", "hangman", "python", "flask"]

    if request.method == "GET":

        session['word'] = random.choice(words).upper()
        session['display'] = "_ " * len(session['word'])
        session['attempts'] = 10
        return render_template("hangman.html", display=session['display'], attempts=session['attempts'])


    if request.method == "POST":
        guess = request.form.get("guess", "").upper()  # Default to empty string if 'guess' is not provided
        word = session['word']
        # Split the display into a list of characters (including spaces)
        display_list = session['display'].split()

        if guess and guess in word:  # Check if guess is not empty and it's in the word
            new_display_list = []
            for w, displayed_char in zip(word, display_list):
                if w == guess:
                    new_display_list.append(guess)
                else:
                    new_display_list.append(displayed_char)
            session['display'] = " ".join(new_display_list)
        else:
            session['attempts'] -= 1

        if "_" not in session['display']:
            return apology("win")  # Display a winning message
        elif session['attempts'] <= 0:
            return apology("loss")  # Display a losing message

        return render_template("hangman.html", display=session['display'], attempts=session['attempts'])


@app.route('/gsq')
@login_required
def gsq():
    """Google Search Query"""
    return apology ("error gsq")

