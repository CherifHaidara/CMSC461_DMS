# dashboard.py
from flask import Blueprint, render_template, session, flash
import mysql.connector
from utils import get_db_connection, login_required

# Define the blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    user_info = {}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get user information with role name
        cursor.execute(
    """
    SELECT 
        u.username,
        e.first_name,
        e.last_name,
        r.role_name
    FROM `USER` u
    LEFT JOIN EMPLOYEE e 
        ON u.employee_id = e.employee_id
    LEFT JOIN ROLE r 
        ON u.role_id = r.role_id
    WHERE u.user_id = %s
    """,
    (session['user_id'],)
)
        user_info = cursor.fetchone() or {}
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
    
    return render_template('dashboard.html', user_id=session['user_id'], user_info=user_info)
