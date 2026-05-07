from flask import Blueprint, render_template, flash, request, redirect, url_for
import mysql.connector
from utils import get_db_connection, login_required, role_required

customer_bp = Blueprint('customer', __name__)


@customer_bp.route('/customers')
@role_required(1, 2)
def customers():

    customers_data = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # JOIN PhoneNumber to get phone alongside customer info.
        # GROUP_CONCAT handles customers with multiple numbers.
        query = """
            SELECT
                c.customer_id,
                c.customer_name,
                c.customer_address,
                c.customer_email,
                GROUP_CONCAT(p.phone_number ORDER BY p.phone_id SEPARATOR ', ') AS customer_phone
            FROM Customer c
            LEFT JOIN PhoneNumber p ON c.customer_id = p.customer_id
            GROUP BY c.customer_id
        """
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
@role_required(1, 2)
def add_customer():

    if request.method == 'POST':

        customer_name    = request.form['customer_name']
        customer_address = request.form['customer_address']
        customer_email   = request.form['customer_email']
        customer_phone   = request.form['customer_phone']

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Step 1: insert the customer (no phone column on this table)
            customer_query = """
                INSERT INTO Customer (customer_name, customer_address, customer_email)
                VALUES (%s, %s, %s)
            """
            cursor.execute(customer_query, (customer_name, customer_address, customer_email))
            new_customer_id = cursor.lastrowid

            # Step 2: insert the phone number into the PhoneNumber table
            if customer_phone:
                phone_query = """
                    INSERT INTO PhoneNumber (phone_number, customer_id)
                    VALUES (%s, %s)
                """
                cursor.execute(phone_query, (customer_phone, new_customer_id))

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
@role_required(1, 2)
def edit_customer(customer_id):

    customer = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':

            customer_name    = request.form['customer_name']
            customer_address = request.form['customer_address']
            customer_email   = request.form['customer_email']
            customer_phone   = request.form['customer_phone']

            # Step 1: update the Customer table (no phone column here)
            update_query = """
                UPDATE Customer
                SET
                    customer_name    = %s,
                    customer_address = %s,
                    customer_email   = %s
                WHERE customer_id = %s
            """
            cursor.execute(update_query, (customer_name, customer_address, customer_email, customer_id))

            # Step 2: upsert the primary phone number in PhoneNumber.
            # If one already exists, update the first record; otherwise insert.
            if customer_phone:
                check_query = """
                    SELECT phone_id FROM PhoneNumber
                    WHERE customer_id = %s
                    ORDER BY phone_id
                    LIMIT 1
                """
                cursor.execute(check_query, (customer_id,))
                existing_phone = cursor.fetchone()

                if existing_phone:
                    phone_query = """
                        UPDATE PhoneNumber
                        SET phone_number = %s
                        WHERE phone_id = %s
                    """
                    cursor.execute(phone_query, (customer_phone, existing_phone['phone_id']))
                else:
                    phone_query = """
                        INSERT INTO PhoneNumber (phone_number, customer_id)
                        VALUES (%s, %s)
                    """
                    cursor.execute(phone_query, (customer_phone, customer_id))

            conn.commit()
            flash("Customer updated successfully.", "success")
            return redirect(url_for('customer.customers'))

        # GET: fetch customer with their primary phone number
        select_query = """
            SELECT
                c.customer_id,
                c.customer_name,
                c.customer_address,
                c.customer_email,
                (
                    SELECT p.phone_number
                    FROM PhoneNumber p
                    WHERE p.customer_id = c.customer_id
                    ORDER BY p.phone_id
                    LIMIT 1
                ) AS customer_phone
            FROM Customer c
            WHERE c.customer_id = %s
        """
        cursor.execute(select_query, (customer_id,))
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
@role_required(1, 2)
def customer_detail(customer_id):

    customer  = None
    purchases = []
    services  = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch customer with all phone numbers
        customer_query = """
            SELECT
                c.customer_id,
                c.customer_name,
                c.customer_address,
                c.customer_email,
                GROUP_CONCAT(p.phone_number ORDER BY p.phone_id SEPARATOR ', ') AS customer_phone
            FROM Customer c
            LEFT JOIN PhoneNumber p ON c.customer_id = p.customer_id
            WHERE c.customer_id = %s
            GROUP BY c.customer_id
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
            FROM Sale s
            JOIN Vehicle v ON s.vehicle_id = v.vehicle_id
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
            JOIN Vehicle v ON sv.vehicle_id = v.vehicle_id
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