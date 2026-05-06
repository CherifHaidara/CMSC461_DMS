from flask import Blueprint, render_template
From Utils import get_db_connection, login_required

customer_bp = Blueprint('customer', __name__)

@customer_bp.route('/customers')
@login required

def customer();

  conn = get_db_connection()
  cursor = conn.cursor()


  query = "SELECT * FROM CUSTOMER" 
  cursor.execute(query)

  customers = cursor.fetchall()

  cursor.close()
  conn.close()

  return render_template('customers.html', customers=customers)
