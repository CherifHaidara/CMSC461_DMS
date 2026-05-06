# auth.py
import hmac
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from utils import get_db_connection
import mysql.connector

# Define the blueprint
auth_bp = Blueprint('auth', __name__)

def _password_matches(stored: str, plain: str) -> bool:
    """Werkzeug hashes from registration, or plain literals from loadAll.sql seed rows."""
    if check_password_hash(stored, plain):
        return True
    if stored.startswith("pbkdf2:") or stored.startswith("scrypt:"):
        return False
    return hmac.compare_digest(stored, plain)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'] 

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM `USER` WHERE username=%s", (username,))
        cursor.execute("SELECT * FROM `USER` WHERE username=%s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and _password_matches(user['password'], password):
            session['user_id'] = user['user_id']
            session['user_role_id'] = user['role_id']
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Invalid username or password. Please try again.", "error")
            return render_template('login.html')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    session.pop('user_id', None)
    session.pop('user_role_id', None)
    flash("You have been successfully logged out.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Handle the form submission
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 1. Hash the password using a secure algorithm (pbkdf2:sha256 by default)
        hashed_password = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 2. Insert the new user into the MySQL database
            # Demo FKs: tie new accounts to employee 10 / sales role (see loadAll.sql seeds).
            cursor.execute(
                "INSERT INTO `USER` (username, password, employee_id, role_id) VALUES (%s, %s, %s, %s)",
                (username, hashed_password, 10, 2),
            )
            # 3. Commit the transaction (required to save INSERT/UPDATE/DELETE changes)
            conn.commit()
            
            # Redirect the user to the login page after successful registration
            flash("You have been successfully registered.", "success")
            return redirect(url_for('auth.login'))
            
        except mysql.connector.IntegrityError:
            # This catches the error if the username already exists due to the UNIQUE constraint
            flash("That username is already taken. Please choose another.", "error")
            return render_template('register.html')
            
        finally:
            # Always close your connections, even if an error occurs
            cursor.close()
            conn.close()

    # If it's a GET request (just visiting the page), show the registration form
    return render_template('register.html')