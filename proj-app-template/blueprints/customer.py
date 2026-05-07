from flask import Blueprint, render_template, flash, request, redirect, url_for
import mysql.connector
from utils import get_db_connection, login_required

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('/customers')
@login_required
def customers():

    customers_data = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Customer"
        cursor.execute(query)

        customers_data = cursor.fetchall()

    except mysql.connector.Error as err:

        flash(f"MySQL Error: {err}", "error")

    finally:

        if 'cursor' in locals() and cursor is not None:
            cursor.close()

        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return render_template(
        'customers.html',
        customers=customers_data
    )


@customer_bp.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():

    if request.method == 'POST':

        customer_name = request.form['customer_name']
        customer_address = request.form['customer_address']
        customer_email = request.form['customer_email']
        customer_phone = request.form['customer_phone']

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                INSERT INTO CUSTOMER
                (
                    customer_name,
                    customer_address,
                    customer_email,
                    customer_phone
                )
                VALUES (%s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    customer_name,
                    customer_address,
                    customer_email,
                    customer_phone
                )
            )

            conn.commit()

            flash("Customer added successfully.", "success")

            return redirect(url_for('customer.customers'))

        except mysql.connector.Error as err:

            flash(f"MySQL Error: {err}", "error")

        finally:

            if 'cursor' in locals() and cursor is not None:
                cursor.close()

            if 'conn' in locals() and conn is not None and conn.is_connected():
                conn.close()

    return render_template('add_customer.html')


@customer_bp.route('/customers/<int:customer_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):

    customer = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':

            customer_name = request.form['customer_name']
            customer_address = request.form['customer_address']
            customer_email = request.form['customer_email']
            customer_phone = request.form['customer_phone']

            query = """
                UPDATE CUSTOMER
                SET
                    customer_name = %s,
                    customer_address = %s,
                    customer_email = %s,
                    customer_phone = %s
                WHERE customer_id = %s
            """

            cursor.execute(
                query,
                (
                    customer_name,
                    customer_address,
                    customer_email,
                    customer_phone,
                    customer_id
                )
            )

            conn.commit()

            flash("Customer updated successfully.", "success")

            return redirect(url_for('customer.customers'))

        query = """
            SELECT *
            FROM CUSTOMER
            WHERE customer_id = %s
        """

        cursor.execute(query, (customer_id,))

        customer = cursor.fetchone()

    except mysql.connector.Error as err:

        flash(f"MySQL Error: {err}", "error")

        return redirect(url_for('customer.customers'))

    finally:

        if 'cursor' in locals() and cursor is not None:
            cursor.close()

        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return render_template(
        'edit_customer.html',
        customer=customer
    )


@customer_bp.route('/customers/<int:customer_id>')
@login_required
def customer_detail(customer_id):

    customer = None
    purchases = []
    services = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        customer_query = """
            SELECT *
            FROM CUSTOMER
            WHERE customer_id = %s
        """

        cursor.execute(customer_query, (customer_id,))
        customer = cursor.fetchone()

        purchases_query = """
            SELECT
                s.sale_id,
                s.sale_price,
                s.sale_date,
                v.vehicle_make,
                v.vehicle_model
            FROM SALE s
            JOIN VEHICLE v
                ON s.vehicle_id = v.vehicle_id
            WHERE s.customer_id = %s
            ORDER BY s.sale_date DESC
        """

        cursor.execute(purchases_query, (customer_id,))
        purchases = cursor.fetchall()

        services_query = """
            SELECT
                sv.service_id,
                sv.service_type,
                sv.service_date,
                sv.service_cost,
                v.vehicle_make,
                v.vehicle_model
            FROM SERVICE sv
            JOIN VEHICLE v
                ON sv.vehicle_id = v.vehicle_id
            WHERE sv.customer_id = %s
            ORDER BY sv.service_date DESC
        """

        cursor.execute(services_query, (customer_id,))
        services = cursor.fetchall()

    except mysql.connector.Error as err:

        flash(f"MySQL Error: {err}", "error")

        return redirect(url_for('customer.customers'))

    finally:

        if 'cursor' in locals() and cursor is not None:
            cursor.close()

        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return render_template(
        'customer_detail.html',
        customer=customer,
        purchases=purchases,
        services=services
    )
