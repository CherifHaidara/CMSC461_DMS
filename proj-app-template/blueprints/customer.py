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
            cursor = conn.cursor()

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
