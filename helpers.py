import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
from cs50 import SQL
import random

import sqlite3

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def hangman_word(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        words_and_points = [(row[1], int(row[2])) for row in reader if row[2].isdigit()]

    word, points = random.choice(words_and_points)
    return word.upper(), points
