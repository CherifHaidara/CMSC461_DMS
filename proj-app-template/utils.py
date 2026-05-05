# utils.py
from functools import wraps
from flask import session, flash, redirect, url_for
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="543210Ta",
        database="car_dealership",
        port=3306
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to be logged in to view this page.", "error")
            # Note the "auth." prefix! We'll explain this in Step 4.
            return redirect(url_for('auth.login')) 
        return f(*args, **kwargs)
    return decorated_function