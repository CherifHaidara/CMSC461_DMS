# auth.py
import hmac
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from utils import get_db_connection
import mysql.connector
from datetime import date

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
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and _password_matches(user['password'], password):
            if user.get('status') != 'Active':
                flash("Your account is deactivated. Please contact an administrator.", "error")
                return render_template('login.html')
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
    departments = []
    roles = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT department_id, department_name FROM DEPARTMENT WHERE status = 'Active' ORDER BY department_name")
        departments = cursor.fetchall()
        cursor.execute("SELECT role_id, role_name FROM ROLE WHERE role_id != 1 ORDER BY role_id")
        roles = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    # Handle the form submission
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        emp_email = request.form['emp_email']
        emp_phone = request.form['emp_phone']
        department_id = request.form['department_id']
        role_id = request.form['role_id']

        if not username or not password or not first_name or not last_name or not emp_email or not emp_phone or not department_id or not role_id:
            flash("All fields are required.", "error")
            return render_template('register.html', departments=departments, roles=roles)

        # 1. Hash the password using a secure algorithm (pbkdf2:sha256 by default)
        hashed_password = generate_password_hash(password)
        
        position = next((role['role_name'] for role in roles if str(role['role_id']) == role_id), 'Staff')

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 2. Insert the new employee into the database
            cursor.execute(
                "INSERT INTO EMPLOYEE (first_name, last_name, emp_email, emp_phone, hire_date, salary, position, department_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (first_name, last_name, emp_email, emp_phone, date.today(), 0.00, position, department_id),
            )
            # Get the new employee_id
            employee_id = cursor.lastrowid
            
            # 3. Insert the new user into the MySQL database
            cursor.execute(
                "INSERT INTO `USER` (username, password, employee_id, role_id, status) VALUES (%s, %s, %s, %s, %s)",
                (username, hashed_password, employee_id, role_id, 'Active'),
            )
            # Get the new user_id
            user_id = cursor.lastrowid
            # 4. Commit the transaction (required to save INSERT/UPDATE/DELETE changes)
            conn.commit()
            
            # Log the user in
            session['user_id'] = user_id
            session['user_role_id'] = int(role_id)
            
            # Redirect the user to the dashboard after successful registration
            flash("You have been successfully registered.", "success")
            return redirect(url_for('dashboard.dashboard'))
            
        except mysql.connector.IntegrityError as e:
            # This catches the error if the username already exists or other integrity issues
            flash(f"Registration failed: {str(e)}", "error")
            return render_template('register.html', departments=departments, roles=roles)
            
        finally:
            # Always close your connections, even if an error occurs
            cursor.close()
            conn.close()

    # If it's a GET request (just visiting the page), show the registration form
    return render_template('register.html', departments=departments, roles=roles)