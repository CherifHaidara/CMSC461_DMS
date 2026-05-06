# directory.py
from flask import Blueprint, render_template, request, session, flash
import mysql.connector
from utils import get_db_connection, login_required, build_pagination

# Define the blueprint
directory_bp = Blueprint('directory', __name__)

@directory_bp.route('/directory')
@login_required
def directory():
    per_page = 10
    page = request.args.get('page', 1, type=int)
    instructors_data = []
    total_items = 0
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM EMPLOYEE")
        total_items = cursor.fetchone()[0]

        pagination = build_pagination(page=page, total_items=total_items, per_page=per_page)
        cursor.execute(
            """
            SELECT CONCAT(e.first_name, ' ', e.last_name), d.department_name
            FROM EMPLOYEE e
            JOIN DEPARTMENT d ON e.department_id = d.department_id
            ORDER BY e.last_name, e.first_name
            LIMIT %s OFFSET %s
            """
            ,
            (pagination["per_page"], pagination["offset"]),
        )
        instructors_data = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        pagination = build_pagination(page=1, total_items=0, per_page=per_page)
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return render_template('directory.html', instructors=instructors_data, pagination=pagination)