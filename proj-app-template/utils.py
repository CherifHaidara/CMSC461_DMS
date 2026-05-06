# utils.py
import os
from functools import wraps
from flask import session, flash, redirect, url_for
import mysql.connector

def get_db_connection():
    """MySQL connection; defaults match docker-compose.yml (override with env vars)."""
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="my-secret-pw",
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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to be logged in to view this page.", "error")
            return redirect(url_for('auth.login'))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT role_id FROM `USER` WHERE user_id=%s", (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user or user['role_id'] != 1:  # role_id 1 is Administrator
            flash("You do not have permission to access this page.", "error")
            return redirect(url_for('dashboard.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function