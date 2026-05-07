# blueprints/sales.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils import get_db_connection, login_required, role_required, build_pagination

sales_bp = Blueprint('sales', __name__)


@sales_bp.route('/sales')
@role_required(1, 2)
def sales_list():
    per_page = 10
    page = request.args.get('page', 1, type=int)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS cnt FROM Sale")
    total_items = cursor.fetchone()["cnt"]
    pagination = build_pagination(page=page, total_items=total_items, per_page=per_page)

    cursor.execute(
        """
        SELECT s.sale_id, s.sale_date, s.sale_price, s.financing_option, s.payment_method,
               c.customer_name,
               CONCAT(v.vehicle_year, ' ', v.vehicle_make, ' ', v.vehicle_model) AS vehicle,
               d.department_name,
               CONCAT(e.first_name, ' ', e.last_name) AS employee_name
        FROM Sale s
        JOIN Customer c ON s.customer_id = c.customer_id
        JOIN Vehicle v ON s.vehicle_id = v.vehicle_id
        JOIN DEPARTMENT d ON s.department_id = d.department_id
        JOIN EMPLOYEE e ON s.employee_id = e.employee_id
        ORDER BY s.sale_date DESC, s.sale_id DESC
        LIMIT %s OFFSET %s
        """,
        (pagination["per_page"], pagination["offset"]),
    )
    sales = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('sales_list.html', sales=sales, pagination=pagination)


@sales_bp.route('/sales/create', methods=['GET', 'POST'])
@role_required(1, 2)
def create_sale():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        customer_id   = request.form['customer_id']
        vehicle_id    = request.form['vehicle_id']
        department_id = request.form['department_id']
        employee_id   = request.form['employee_id']
        sale_date     = request.form['sale_date']
        sale_price    = request.form['sale_price']
        financing_option = request.form['financing_option']
        payment_method   = request.form['payment_method']

        try:
            cursor.execute(
                """
                INSERT INTO Sale
                    (sale_date, sale_price, financing_option, payment_method,
                     vehicle_id, customer_id, department_id, employee_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (sale_date, sale_price, financing_option, payment_method,
                 vehicle_id, customer_id, department_id, employee_id),
            )
            # Capture sale_id NOW before the UPDATE overwrites cursor.lastrowid
            sale_id = cursor.lastrowid
            # Automatically mark vehicle as sold
            cursor.execute(
                "UPDATE Vehicle SET vehicle_availability_status = 'sold' WHERE vehicle_id = %s",
                (vehicle_id,),
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash("Sale recorded successfully.", "success")
            return redirect(url_for('sales.sale_detail', sale_id=sale_id))
        except Exception as e:
            conn.rollback()
            flash(f"Error creating sale: {e}", "error")

    cursor.execute("SELECT customer_id, customer_name FROM Customer ORDER BY customer_name")
    customers = cursor.fetchall()

    cursor.execute(
        """
        SELECT vehicle_id,
               CONCAT(vehicle_year, ' ', vehicle_make, ' ', vehicle_model, ' — ', vehicle_vin) AS label,
               vehicle_price
        FROM Vehicle
        WHERE vehicle_availability_status = 'available'
        ORDER BY vehicle_year DESC, vehicle_make
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
        'create_sale.html',
        customers=customers,
        vehicles=vehicles,
        departments=departments,
        employees=employees,
    )


@sales_bp.route('/sales/<int:sale_id>')
@role_required(1, 2)
def sale_detail(sale_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT s.*,
               c.customer_name, c.customer_email, c.customer_address,
               CONCAT(v.vehicle_year, ' ', v.vehicle_make, ' ', v.vehicle_model) AS vehicle_label,
               v.vehicle_vin, v.vehicle_condition,
               d.department_name,
               CONCAT(e.first_name, ' ', e.last_name) AS employee_name,
               e.emp_email, e.position
        FROM Sale s
        JOIN Customer c ON s.customer_id = c.customer_id
        JOIN Vehicle v ON s.vehicle_id = v.vehicle_id
        JOIN DEPARTMENT d ON s.department_id = d.department_id
        JOIN EMPLOYEE e ON s.employee_id = e.employee_id
        WHERE s.sale_id = %s
        """,
        (sale_id,),
    )
    sale = cursor.fetchone()
    cursor.close()
    conn.close()

    if not sale:
        flash("Sale not found.", "error")
        return redirect(url_for('sales.sales_list'))

    return render_template('sale_detail.html', sale=sale)