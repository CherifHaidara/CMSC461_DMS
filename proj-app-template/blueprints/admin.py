# admin.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash
import mysql.connector
from utils import get_db_connection, admin_required, build_pagination
from datetime import date

# Define the blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/')
@admin_required
def admin_home():
    return redirect(url_for('admin.view_users'))


@admin_bp.route('/users')
@admin_required
def view_users():
    """Display all users in the system."""
    per_page = 10
    page = request.args.get('page', 1, type=int)
    users_data = []
    total_items = 0
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS cnt FROM `USER`")
        total_items = cursor.fetchone()["cnt"]
        pagination = build_pagination(page=page, total_items=total_items, per_page=per_page)
        cursor.execute(
            """
            SELECT u.user_id, u.username, u.employee_id, e.first_name, e.last_name, 
                   r.role_id, r.role_name, u.status
            FROM `USER` u
            JOIN EMPLOYEE e ON u.employee_id = e.employee_id
            JOIN ROLE r ON u.role_id = r.role_id
            ORDER BY u.employee_id ASC
            LIMIT %s OFFSET %s
            """,
            (pagination["per_page"], pagination["offset"]),
        )
        users_data = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        pagination = build_pagination(page=1, total_items=0, per_page=per_page)
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return render_template(
        'admin/view_users.html',
        users=users_data,
        admin_tab='users',
        pagination=pagination,
    )


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@admin_required
def create_user():
    """Create a new user."""
    departments = []
    roles_data = []
    
    # Fetch departments and roles for dropdowns
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT department_id, department_name FROM DEPARTMENT WHERE status = 'Active' ORDER BY department_name")
        departments = cursor.fetchall()
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
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        emp_email = request.form.get('emp_email', '').strip()
        emp_phone = request.form.get('emp_phone', '').strip()
        department_id = request.form.get('department_id', '').strip()
        role_id = request.form.get('role_id', '').strip()

        if not all([username, password, first_name, last_name, emp_email, emp_phone, department_id, role_id]):
            flash("All fields are required.", "error")
            return render_template(
                'admin/create_user.html',
                departments=departments,
                roles=roles_data,
                admin_tab='users',
            )

        selected_role = next((role for role in roles_data if str(role['role_id']) == role_id), None)
        position = selected_role['role_name'] if selected_role else 'Staff'

        try:
            hashed_password = generate_password_hash(password)
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Insert employee
            cursor.execute(
                "INSERT INTO EMPLOYEE (first_name, last_name, emp_email, emp_phone, hire_date, salary, position, department_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (first_name, last_name, emp_email, emp_phone, date.today(), 0.00, position, department_id),
            )
            employee_id = cursor.lastrowid
            
            # Insert user
            cursor.execute(
                "INSERT INTO `USER` (username, password, employee_id, role_id, status) VALUES (%s, %s, %s, %s, %s)",
                (username, hashed_password, employee_id, role_id, 'Active')
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

    return render_template(
        'admin/create_user.html',
        departments=departments,
        roles=roles_data,
        admin_tab='users',
    )


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    departments = []
    roles_data = []
    user_data = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT u.user_id, u.username, u.employee_id, u.role_id, u.status, e.first_name, e.last_name, e.emp_email, e.emp_phone, e.department_id "
            "FROM `USER` u JOIN EMPLOYEE e ON u.employee_id = e.employee_id WHERE u.user_id = %s",
            (user_id,)
        )
        user_data = cursor.fetchone()

        if not user_data:
            flash("User not found.", "error")
            return redirect(url_for('admin.view_users'))

        cursor.execute("SELECT department_id, department_name FROM DEPARTMENT WHERE status = 'Active' ORDER BY department_name")
        departments = cursor.fetchall()

        cursor.execute("SELECT role_id, role_name FROM ROLE ORDER BY role_id")
        roles_data = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        return redirect(url_for('admin.view_users'))
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        emp_email = request.form.get('emp_email', '').strip()
        emp_phone = request.form.get('emp_phone', '').strip()
        department_id = request.form.get('department_id', '').strip()
        role_id = request.form.get('role_id', '').strip()

        if not username or not first_name or not last_name or not emp_email or not emp_phone or not department_id or not role_id:
            flash("All fields are required.", "error")
            return render_template(
                'admin/edit_user.html',
                user=user_data,
                departments=departments,
                roles=roles_data,
                admin_tab='users',
            )

        selected_role = next((role for role in roles_data if str(role['role_id']) == role_id), None)
        position = selected_role['role_name'] if selected_role else 'Staff'

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            if password:
                hashed_password = generate_password_hash(password)
                cursor.execute(
                    "UPDATE `USER` SET username=%s, password=%s, role_id=%s WHERE user_id=%s",
                    (username, hashed_password, role_id, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE `USER` SET username=%s, role_id=%s WHERE user_id=%s",
                    (username, role_id, user_id)
                )

            cursor.execute(
                "UPDATE EMPLOYEE SET first_name=%s, last_name=%s, emp_email=%s, emp_phone=%s, position=%s, department_id=%s WHERE employee_id=%s",
                (first_name, last_name, emp_email, emp_phone, position, department_id, user_data['employee_id'])
            )
            conn.commit()
            flash("User updated successfully.", "success")
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

        user_data.update({
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'emp_email': emp_email,
            'emp_phone': emp_phone,
            'department_id': department_id,
            'role_id': int(role_id),
        })

    return render_template(
        'admin/edit_user.html',
        user=user_data,
        departments=departments,
        roles=roles_data,
        admin_tab='users',
    )


@admin_bp.route('/users/<int:user_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_user(user_id):
    if user_id == session['user_id']:
        flash("You cannot deactivate your own account.", "error")
        return redirect(url_for('admin.view_users'))
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE `USER` SET status = 'Inactive' WHERE user_id = %s", (user_id,))
        conn.commit()
        if cursor.rowcount:
            flash("User deactivated successfully.", "success")
        else:
            flash("User not found.", "error")
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return redirect(url_for('admin.view_users'))


@admin_bp.route('/users/<int:user_id>/activate', methods=['POST'])
@admin_required
def activate_user(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE `USER` SET status = 'Active' WHERE user_id = %s", (user_id,))
        conn.commit()
        if cursor.rowcount:
            flash("User reactivated successfully.", "success")
        else:
            flash("User not found.", "error")
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return redirect(url_for('admin.view_users'))


@admin_bp.route('/divisions')
@admin_required
def view_divisions():
    """Display all divisions and departments."""
    divisions_data = []
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
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
        
        for division in divisions_data:
            if division['departments']:
                dept_list = []
                dept_strings = division['departments'].split('|||')
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

    return render_template('admin/view_divisions.html', divisions=divisions_data, admin_tab='divisions')


@admin_bp.route('/divisions/create', methods=['GET', 'POST'])
@admin_required
def create_division():
    if request.method == 'POST':
        division_name = request.form.get('division_name', '').strip()
        description = request.form.get('description', '').strip()

        if not division_name:
            flash("Division name is required.", "error")
            return render_template('admin/create_division.html', admin_tab='divisions')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO DIVISION (division_name, description) VALUES (%s, %s)",
                (division_name, description)
            )
            conn.commit()
            flash("Division created successfully.", "success")
            return redirect(url_for('admin.view_divisions'))
        except mysql.connector.Error as err:
            flash(f"MySQL Error: {err}", "error")
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn is not None and conn.is_connected():
                conn.close()

    return render_template('admin/create_division.html', admin_tab='divisions')


@admin_bp.route('/divisions/<int:division_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_division(division_id):
    division = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT division_id, division_name, description FROM DIVISION WHERE division_id = %s",
            (division_id,)
        )
        division = cursor.fetchone()
        if not division:
            flash("Division not found.", "error")
            return redirect(url_for('admin.view_divisions'))
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        return redirect(url_for('admin.view_divisions'))
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    if request.method == 'POST':
        division_name = request.form.get('division_name', '').strip()
        description = request.form.get('description', '').strip()

        if not division_name:
            flash("Division name is required.", "error")
            return render_template('admin/edit_division.html', division=division, admin_tab='divisions')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE DIVISION SET division_name = %s, description = %s WHERE division_id = %s",
                (division_name, description, division_id)
            )
            conn.commit()
            flash("Division updated successfully.", "success")
            return redirect(url_for('admin.view_divisions'))
        except mysql.connector.Error as err:
            flash(f"MySQL Error: {err}", "error")
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn is not None and conn.is_connected():
                conn.close()

    return render_template('admin/edit_division.html', division=division, admin_tab='divisions')


@admin_bp.route('/divisions/<int:division_id>/delete', methods=['POST'])
@admin_required
def delete_division(division_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM DEPARTMENT WHERE division_id = %s", (division_id,))
        cursor.execute("DELETE FROM DIVISION WHERE division_id = %s", (division_id,))
        conn.commit()
        flash("Division removed successfully.", "success")
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return redirect(url_for('admin.view_divisions'))


@admin_bp.route('/departments/create', methods=['GET', 'POST'])
@admin_required
def create_department():
    divisions_data = []
    selected_division_id = request.args.get('division_id', type=int)
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT division_id, division_name FROM DIVISION ORDER BY division_name")
        divisions_data = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    if request.method == 'POST':
        department_name = request.form.get('department_name', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'Active').strip()
        division_id = request.form.get('division_id', '').strip()

        if not department_name or not division_id:
            flash("Department name and division are required.", "error")
            return render_template(
                'admin/create_department.html',
                divisions=divisions_data,
                selected_division_id=selected_division_id,
                admin_tab='divisions',
            )

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO DEPARTMENT (department_name, description, status, division_id) VALUES (%s, %s, %s, %s)",
                (department_name, description, status, division_id)
            )
            conn.commit()
            flash("Department created successfully.", "success")
            return redirect(url_for('admin.view_divisions'))
        except mysql.connector.Error as err:
            flash(f"MySQL Error: {err}", "error")
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn is not None and conn.is_connected():
                conn.close()

    return render_template(
        'admin/create_department.html',
        divisions=divisions_data,
        selected_division_id=selected_division_id,
        admin_tab='divisions',
    )


@admin_bp.route('/departments/<int:department_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_department(department_id):
    divisions_data = []
    department = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT division_id, division_name FROM DIVISION ORDER BY division_name")
        divisions_data = cursor.fetchall()
        cursor.execute(
            "SELECT department_id, department_name, description, status, division_id FROM DEPARTMENT WHERE department_id = %s",
            (department_id,)
        )
        department = cursor.fetchone()
        if not department:
            flash("Department not found.", "error")
            return redirect(url_for('admin.view_divisions'))
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
        return redirect(url_for('admin.view_divisions'))
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    if request.method == 'POST':
        department_name = request.form.get('department_name', '').strip()
        description = request.form.get('description', '').strip()
        status = request.form.get('status', 'Active').strip()
        division_id = request.form.get('division_id', '').strip()

        if not department_name or not division_id or not status:
            flash("Department name, division, and status are required.", "error")
            return render_template(
                'admin/edit_department.html',
                department=department,
                divisions=divisions_data,
                admin_tab='divisions',
            )

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE DEPARTMENT SET department_name = %s, description = %s, status = %s, division_id = %s WHERE department_id = %s",
                (department_name, description, status, division_id, department_id)
            )
            conn.commit()
            flash("Department updated successfully.", "success")
            return redirect(url_for('admin.view_divisions'))
        except mysql.connector.Error as err:
            flash(f"MySQL Error: {err}", "error")
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn is not None and conn.is_connected():
                conn.close()

    return render_template(
        'admin/edit_department.html',
        department=department,
        divisions=divisions_data,
        admin_tab='divisions',
    )


@admin_bp.route('/departments/<int:department_id>/deactivate', methods=['POST'])
@admin_required
def deactivate_department(department_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE DEPARTMENT SET status = 'Inactive' WHERE department_id = %s", (department_id,))
        conn.commit()
        if cursor.rowcount:
            flash("Department deactivated successfully.", "success")
        else:
            flash("Department not found.", "error")
    except mysql.connector.Error as err:
        flash(f"MySQL Error: {err}", "error")
    finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()
        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return redirect(url_for('admin.view_divisions'))
