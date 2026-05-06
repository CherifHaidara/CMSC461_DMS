# admin.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
import mysql.connector
from utils import get_db_connection, admin_required

# Define the blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/users')
@admin_required
def view_users():
    """Display all users in the system."""
    users_data = []
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT u.user_id, u.username, u.employee_id, e.first_name, e.last_name, 
                   r.role_id, r.role_name
            FROM `USER` u
            JOIN EMPLOYEE e ON u.employee_id = e.employee_id
            JOIN ROLE r ON u.role_id = r.role_id
            ORDER BY u.username
            """
        )
        users_data = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return render_template('admin/view_users.html', users=users_data)


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Create a new user."""
    employees_data = []
    roles_data = []
    
    # Fetch employees and roles for dropdown menus
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all employees
        cursor.execute(
            """
            SELECT e.employee_id, CONCAT(e.first_name, ' ', e.last_name) as full_name
            FROM EMPLOYEE e
            ORDER BY e.last_name, e.first_name
            """
        )
        employees_data = cursor.fetchall()
        
        # Get all roles
        cursor.execute("SELECT role_id, role_name FROM ROLE ORDER BY role_id")
        roles_data = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        employee_id = request.form.get('employee_id', '').strip()
        role_id = request.form.get('role_id', '').strip()

        # Validate input
        if not username or not password or not employee_id or not role_id:
            flash("All fields are required.", "error")
            return render_template('admin/create_user.html', employees=employees_data, roles=roles_data)

        try:
            # Hash password
            hashed_password = generate_password_hash(password)
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert the new user
            cursor.execute(
                "INSERT INTO `USER` (username, password, employee_id, role_id) VALUES (%s, %s, %s, %s)",
                (username, hashed_password, employee_id, role_id)
            )
            conn.commit()
            
            flash(f"User '{username}' created successfully.", "success")
            return redirect(url_for('admin.view_users'))
            
        except mysql.connector.IntegrityError as e:
            if "username" in str(e).lower():
                flash("Username already exists. Please choose another.", "error")
            else:
                flash(f"Database Error: {e}", "error")
        except mysql.connector.Error as err:
            flash(f"MySQL Error: {err}", "error")
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn is not None and conn.is_connected():
                conn.close()

    return render_template('admin/create_user.html', employees=employees_data, roles=roles_data)


@admin_bp.route('/divisions')
@admin_required
def view_divisions():
    """Display all divisions and departments."""
    divisions_data = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get all divisions with their departments
        cursor.execute(
            """
            SELECT d.division_id, d.division_name, d.description, 
                   GROUP_CONCAT(CONCAT(dept.department_id, '|||', dept.department_name, '|||', 
                                       dept.description, '|||', dept.status) SEPARATOR '|||') as departments
            FROM DIVISION d
            LEFT JOIN DEPARTMENT dept ON d.division_id = dept.division_id
            GROUP BY d.division_id, d.division_name, d.description
            ORDER BY d.division_id
            """
        )
        divisions_data = cursor.fetchall()
        
        # Parse the departments data
        for division in divisions_data:
            if division['departments']:
                dept_list = []
                dept_strings = division['departments'].split('|||')
                # Process in groups of 4
                for i in range(0, len(dept_strings), 4):
                    if i + 3 < len(dept_strings):
                        dept_list.append({
                            'department_id': dept_strings[i],
                            'department_name': dept_strings[i + 1],
                            'description': dept_strings[i + 2],
                            'status': dept_strings[i + 3]
                        })
                division['dept_list'] = dept_list
            else:
                division['dept_list'] = []
                
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return render_template('admin/view_divisions.html', divisions=divisions_data)
