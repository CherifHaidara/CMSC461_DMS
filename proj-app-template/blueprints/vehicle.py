from flask import Blueprint, render_template
import mysql.connector
from utils import get_db_connection, login_required

vehicle_bp = Blueprint('vehicle', __name__)

@vehicle_bp.route('/vehicles')
@login required

def vehicles();

  vehicles_data = []

  try:
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM VEHICLE" 
    cursor.execute(query)

  except mysql.connector.Error as err:
    flash(f"MySQL Error: {err}", "error")
    
   finally:
        if 'cursor' in locals() and cursor is not None:
            cursor.close()

        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return render_template(
        'vehicles.html',
        vehicles=vehicles_data
    )
