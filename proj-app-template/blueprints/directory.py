# directory.py
from flask import Blueprint, render_template, session, flash
import mysql.connector
from utils import get_db_connection, login_required

# Define the blueprint
directory_bp = Blueprint('directory', __name__)

@directory_bp.route('/directory')
@login_required
def directory():
    instructors_data = [] 
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT CONCAT(e.first_name, ' ', e.last_name), d.department_name
            FROM EMPLOYEE e
            JOIN DEPARTMENT d ON e.department_id = d.department_id
            ORDER BY e.last_name, e.first_name
            """
        )
        instructors_data = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return render_template('directory.html', instructors=instructors_data)