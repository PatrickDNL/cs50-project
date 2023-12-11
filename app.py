import os

import sqlite3
import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import random

from helpers import apology, login_required, hangman_word



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

            user_id = session.get("user_id")
            db.execute("INSERT INTO game_rounds (user_id, timestamp, game, input, result, points) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, datetime.datetime.now(), "Rock Paper Scissors", choice, "tie", 0)

        elif (choice == "rock" and comp_choice == "scissors") or \
             (choice == "scissors" and comp_choice == "paper") or \
             (choice == "paper" and comp_choice == "rock"):
            session['score_you'] += 1
            result = "win"

            user_id = session.get("user_id")
            db.execute("INSERT INTO game_rounds (user_id, timestamp, game, input, result, points) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, datetime.datetime.now(), "Rock Paper Scissors", choice, "win", 1)

        else:
            session['score_ai'] += 1
            result = "lose"

            user_id = session.get("user_id")
            db.execute("INSERT INTO game_rounds (user_id, timestamp, game, input, result, points) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, datetime.datetime.now(), "Rock Paper Scissors", choice, "loss", -1)


        player_image = f"you_{choice}.png"
        comp_image = f"comp_{comp_choice}.png"

        return render_template("rps.html", result=result, ai=session['score_ai'], you=session['score_you'], player_image=player_image, comp_image=comp_image)


@app.route('/hl', methods=["GET", "POST"])
@login_required
def hl():
    """higher lower"""

    win = False
    loss = False

    if 'score' not in session:
        session['score'] = 0

    if request.method == "POST":
        random_number_ai = random.randint(1, 100)
        choice = request.form.get("choice")

        # Retrieve the last random number from the session
        random_number = session.get('random_number', 0)

        if (choice == "higher" and random_number < random_number_ai) or \
           (choice == "lower" and random_number > random_number_ai):
            session['score'] += 1
            win = True

            user_id = session.get("user_id")
            db.execute("INSERT INTO game_rounds (user_id, timestamp, game, input, result, points) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, datetime.datetime.now(), "Higher Lower", choice, "win", 1)

        elif choice == "tie" and random_number == random_number_ai:
            win = True

            user_id = session.get("user_id")
            db.execute("INSERT INTO game_rounds (user_id, timestamp, game, input, result, points) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, datetime.datetime.now(), "Higher Lower", choice, "win", 100)

        else:
            loss = True

            user_id = session.get("user_id")
            db.execute("INSERT INTO game_rounds (user_id, timestamp, game, input, result, points) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, datetime.datetime.now(), "Higher Lower", choice, "loss", -1)

        # Generate a new random number for the next round
        session['random_number'] = random.randint(1, 100)

    else:  # This is a GET request
        if 'random_number' not in session:  # Only generate if not already present
            session['random_number'] = random.randint(1, 100)

    # Render template for both GET and POST requests
    return render_template("hl.html", random_number=session['random_number'],
                           win=win, loss=loss, score=session['score'])

@app.route('/hangman', methods=["GET", "POST"])
@login_required
def hangman():
    """hangman"""

    word, points = hangman_word('/workspaces/118817954/project/dictionary.csv')

    if request.method == "GET":

        session['word'] = word
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

        win = False
        loss = False

        if "_" not in session['display']:
            win = True  # Display a winning message

            user_id = session.get("user_id")
            db.execute("INSERT INTO game_rounds (user_id, timestamp, game, input, result, points) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, datetime.datetime.now(), "Hangman", word, "win", points)

        elif session['attempts'] <= 0:
            loss = True

            user_id = session.get("user_id")
            db.execute("INSERT INTO game_rounds (user_id, timestamp, game, input, result, points) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, datetime.datetime.now(), "Hangman", word, "Loss", -points)

        return render_template("hangman.html", display=session['display'], attempts=session['attempts'], win=win, loss=loss, word=word)


@app.route('/statistics')
@login_required
def statistics():

    # Calculate pick rate for Rock Paper Scissors
    pick_rate_rps = db.execute("SELECT input, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM game_rounds WHERE game = 'Rock Paper Scissors') AS percentage FROM game_rounds WHERE game = 'Rock Paper Scissors' GROUP BY input")

    # Calculate win/tie/loss rate per input for Rock Paper Scissors
    win_rate_rps = db.execute("SELECT g.input, g.result, COUNT(g.result) AS count, COUNT(g.result) * 100.0 / t.total_count AS percentage FROM game_rounds AS g JOIN (SELECT input, COUNT(*) AS total_count FROM game_rounds WHERE game = 'Rock Paper Scissors' GROUP BY input) AS t ON g.input = t.input WHERE g.game = 'Rock Paper Scissors' GROUP BY g.input, g.result")

    # Calculate pick rate of higer lower
    pick_rate_hl = db.execute("SELECT input, COUNT(*) * 100.0 / (SELECT COUNT(*) FROM game_rounds WHERE game = 'Higher Lower') AS percentage FROM game_rounds WHERE game = 'Higher Lower' GROUP BY input")

    # Calculate win rate higher / tie / loss
    win_rate_hl = db.execute("SELECT g.input, g.result, COUNT(g.result) AS count, COUNT(g.result) * 100.0 / t.total_count AS percentage FROM game_rounds AS g JOIN (SELECT input, COUNT(*) AS total_count FROM game_rounds WHERE game = 'Higher Lower' GROUP BY input) AS t ON g.input = t.input WHERE g.game = 'Higher Lower' GROUP BY g.input, g.result")

    # Calculate avg. points per input
    avg_pt_hl = db.execute("SELECT g.input, AVG(g.points) AS avg_points FROM game_rounds AS g WHERE g.game = 'Higher Lower' GROUP BY g.input")

    # Word count
    word_count = db.execute("SELECT input, COUNT(input) AS input_count FROM game_rounds WHERE game = 'Hangman' GROUP BY input ORDER BY input_count DESC limit 10;")

    # Pass the entire pick_rate_rps list to the template
    return render_template("statistics.html", pick_rate_rps=pick_rate_rps, win_rate_rps=win_rate_rps, pick_rate_hl=pick_rate_hl, win_rate_hl=win_rate_hl, avg_pt_hl=avg_pt_hl, word_count=word_count)

@app.route('/highscore')
@login_required
def highscore():
    """Show highscores for various games."""

    # Overall high scores
    o_highscore = db.execute("""SELECT u.username, SUM(gr.points) AS total_points FROM game_rounds gr JOIN users u ON gr.user_id = u.id GROUP BY u.username ORDER BY SUM(gr.points) DESC LIMIT 10 """)

    # Rock Paper Scissors high scores
    r_highscore = db.execute("""SELECT u.username, SUM(gr.points) AS total_points FROM game_rounds gr JOIN users u ON gr.user_id = u.id WHERE gr.game = 'Rock Paper Scissors' GROUP BY u.username ORDER BY SUM(gr.points) DESC LIMIT 10 """)

    # Higher Lower high scores
    hl_highscore = db.execute("""SELECT u.username, SUM(gr.points) AS total_points FROM game_rounds gr JOIN users u ON gr.user_id = u.id WHERE gr.game = 'Higher Lower' GROUP BY u.username ORDER BY SUM(gr.points) DESC LIMIT 10 """)

    # Hangman high scores
    h_highscore = db.execute("""SELECT u.username, SUM(gr.points) AS total_points FROM game_rounds gr JOIN users u ON gr.user_id = u.id WHERE gr.game = 'Hangman' GROUP BY u.username ORDER BY SUM(gr.points) DESC LIMIT 10 """)

    # Pass the high scores to the template
    return render_template("highscore.html", o_highscore=o_highscore, r_highscore=r_highscore, hl_highscore=hl_highscore, h_highscore=h_highscore)


@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    """profile info"""

    user_id = session.get("user_id")

    if request.method == "GET":
        # Fetch all user details with a single query
        user_details = db.execute("SELECT username, first_name, last_name, email, country, city, birthdate FROM users WHERE id = ?", user_id)

        # Check if the user details were found
        if user_details:
            # user_details[0] contains the user's information
            return render_template("profile.html",
                                username=user_details[0]['username'],
                                first_name=user_details[0]['first_name'],
                                last_name=user_details[0]['last_name'],
                                email=user_details[0]['email'],
                                country=user_details[0]['country'],
                                city=user_details[0]['city'],
                                DoB=user_details[0]['birthdate'])

    if request.method == "POST":
        # Extract form data
        user_id = session.get("user_id")
        user_result = db.execute("SELECT username FROM users WHERE id = ?", user_id)
        username = user_result[0]['username']

        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        country = request.form.get('country')
        city = request.form.get('city')
        birthdate = request.form.get('birthdate')

        # Validate that user_id and all form fields are available
        if user_id and first_name and last_name and email and country and city and birthdate:
            # Update user details in the database
            db.execute("UPDATE users SET first_name = ?, last_name = ?, email = ?, country = ?, city = ?, birthdate = ? WHERE username = ?",
                        first_name, last_name, email, country, city, birthdate, username)

            # Redirect to the profile page to view the changes or show a success message
            return redirect('/profile')
