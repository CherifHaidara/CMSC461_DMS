# blueprints/service.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils import get_db_connection, login_required, build_pagination

service_bp = Blueprint('service', __name__)


@service_bp.route('/services')
@login_required
def service_list():
    per_page = 10
    page = request.args.get('page', 1, type=int)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS cnt FROM SERVICE")
    total_items = cursor.fetchone()["cnt"]
    pagination = build_pagination(page=page, total_items=total_items, per_page=per_page)

    cursor.execute(
        """
        SELECT sv.service_id, sv.service_type, sv.service_date, sv.service_cost,
               c.customer_name,
               CONCAT(v.vehicle_year, ' ', v.vehicle_make, ' ', v.vehicle_model) AS vehicle,
               CONCAT(e.first_name, ' ', e.last_name) AS technician
        FROM SERVICE sv
        JOIN Customer c ON sv.customer_id = c.customer_id
        JOIN Vehicle v ON sv.vehicle_id = v.vehicle_id
        JOIN EMPLOYEE e ON sv.employee_id = e.employee_id
        ORDER BY sv.service_date DESC, sv.service_id DESC
        LIMIT %s OFFSET %s
        """,
        (pagination["per_page"], pagination["offset"]),
    )
    services = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('service_list.html', services=services, pagination=pagination)


@service_bp.route('/services/create', methods=['GET', 'POST'])
@login_required
def create_service():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        customer_id   = request.form['customer_id']
        vehicle_id    = request.form['vehicle_id']
        department_id = request.form['department_id']
        employee_id   = request.form['employee_id']
        service_type  = request.form['service_type']
        service_date  = request.form['service_date']
        service_cost  = request.form['service_cost']

        try:
            cursor.execute(
                """
                INSERT INTO SERVICE
                    (service_type, service_date, service_cost,
                     customer_id, vehicle_id, employee_id, department_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (service_type, service_date, service_cost,
                 customer_id, vehicle_id, employee_id, department_id),
            )
            conn.commit()
            service_id = cursor.lastrowid
            cursor.close()
            conn.close()
            flash("Service record created successfully.", "success")
            return redirect(url_for('service.service_detail', service_id=service_id))
        except Exception as e:
            conn.rollback()
            flash(f"Error creating service record: {e}", "error")

    cursor.execute("SELECT customer_id, customer_name FROM Customer ORDER BY customer_name")
    customers = cursor.fetchall()

    cursor.execute(
        """
        SELECT vehicle_id,
               CONCAT(vehicle_year, ' ', vehicle_make, ' ', vehicle_model, ' (', vehicle_vin, ')') AS label
        FROM Vehicle ORDER BY vehicle_year DESC, vehicle_make
        """
    )
    vehicles = cursor.fetchall()

    cursor.execute("SELECT department_id, department_name FROM DEPARTMENT ORDER BY department_name")
    departments = cursor.fetchall()

    cursor.execute(
        "SELECT employee_id, CONCAT(first_name, ' ', last_name) AS name FROM EMPLOYEE ORDER BY last_name"
    )
    employees = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template(
        'create_service.html',
        customers=customers,
        vehicles=vehicles,
        departments=departments,
        employees=employees,
    )


@service_bp.route('/services/<int:service_id>')
@login_required
def service_detail(service_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT sv.*,
               c.customer_name, c.customer_email,
               CONCAT(v.vehicle_year, ' ', v.vehicle_make, ' ', v.vehicle_model) AS vehicle_label,
               v.vehicle_vin,
               d.department_name,
               CONCAT(e.first_name, ' ', e.last_name) AS technician,
               e.position
        FROM SERVICE sv
        JOIN Customer c ON sv.customer_id = c.customer_id
        JOIN Vehicle v ON sv.vehicle_id = v.vehicle_id
        JOIN DEPARTMENT d ON sv.department_id = d.department_id
        JOIN EMPLOYEE e ON sv.employee_id = e.employee_id
        WHERE sv.service_id = %s
        """,
        (service_id,),
    )
    service = cursor.fetchone()

    if not service:
        cursor.close()
        conn.close()
        flash("Service record not found.", "error")
        return redirect(url_for('service.service_list'))

    cursor.execute(
        "SELECT * FROM SERVICE_PART WHERE service_id = %s ORDER BY service_part_id",
        (service_id,),
    )
    parts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('service_detail.html', service=service, parts=parts)


@service_bp.route('/services/<int:service_id>/parts/add', methods=['GET', 'POST'])
@login_required
def add_part(service_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT sv.service_id, sv.service_type, sv.service_date,
               CONCAT(v.vehicle_year, ' ', v.vehicle_make, ' ', v.vehicle_model) AS vehicle_label
        FROM SERVICE sv
        JOIN Vehicle v ON sv.vehicle_id = v.vehicle_id
        WHERE sv.service_id = %s
        """,
        (service_id,),
    )
    service = cursor.fetchone()

    if not service:
        cursor.close()
        conn.close()
        flash("Service record not found.", "error")
        return redirect(url_for('service.service_list'))

    if request.method == 'POST':
        part_name = request.form['part_name']
        quantity  = request.form['quantity']
        part_cost = request.form['part_cost']

        try:
            cursor.execute(
                """
                INSERT INTO SERVICE_PART (part_name, quantity, part_cost, service_id)
                VALUES (%s, %s, %s, %s)
                """,
                (part_name, quantity, part_cost, service_id),
            )
            conn.commit()
            flash("Part added successfully.", "success")
            cursor.close()
            conn.close()
            return redirect(url_for('service.service_detail', service_id=service_id))
        except Exception as e:
            conn.rollback()
            flash(f"Error adding part: {e}", "error")

    cursor.close()
    conn.close()
    return render_template('add_part.html', service=service)


@service_bp.route('/vehicles/<int:vehicle_id>/history')
@login_required
def vehicle_history(vehicle_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT vehicle_id, vehicle_year, vehicle_make, vehicle_model,
               vehicle_vin, vehicle_mileage, vehicle_condition, vehicle_availability_status
        FROM Vehicle WHERE vehicle_id = %s
        """,
        (vehicle_id,),
    )
    vehicle = cursor.fetchone()

    if not vehicle:
        cursor.close()
        conn.close()
        flash("Vehicle not found.", "error")
        return redirect(url_for('service.service_list'))

    cursor.execute(
        """
        SELECT sv.service_id, sv.service_type, sv.service_date, sv.service_cost,
               c.customer_name,
               CONCAT(e.first_name, ' ', e.last_name) AS technician,
               d.department_name,
               (SELECT COUNT(*) FROM SERVICE_PART sp WHERE sp.service_id = sv.service_id) AS parts_count,
               (SELECT COALESCE(SUM(sp.part_cost * sp.quantity), 0)
                FROM SERVICE_PART sp WHERE sp.service_id = sv.service_id) AS parts_total
        FROM SERVICE sv
        JOIN Customer c ON sv.customer_id = c.customer_id
        JOIN EMPLOYEE e ON sv.employee_id = e.employee_id
        JOIN DEPARTMENT d ON sv.department_id = d.department_id
        WHERE sv.vehicle_id = %s
        ORDER BY sv.service_date DESC
        """,
        (vehicle_id,),
    )
    history = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('vehicle_history.html', vehicle=vehicle, history=history)