from flask import Blueprint, render_template
From Utils import get_db_connection, login_required

customer_bp = Blueprint('vehicle', __name__)

@customer_bp.route('/vehicles')
@login required

def vehicles();

  conn = get_db_connection()
  cursor = conn.cursor()


  query = "SELECT * FROM VEHICLE" 
  cursor.execute(query)

  customers = cursor.fetchall()

  cursor.close()
  conn.close()

  return render_template('customers.html', vehicles=vehicles)
