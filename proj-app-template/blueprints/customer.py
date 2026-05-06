from flask import Blueprint, render_template, flash
import mysql.connector
from utils import get_db_connection, login_required

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customers')
@login required

def customer();

  customers_data = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM CUSTOMER"
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
