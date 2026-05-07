from flask import Blueprint, render_template, flash, request, redirect, url_for
import mysql.connector
from utils import get_db_connection, login_required

vehicle_bp = Blueprint('vehicle', __name__)


@vehicle_bp.route('/vehicles')
@login_required
def vehicles():

    vehicles_data = []

    make = request.args.get('make', '')
    model = request.args.get('model', '')
    year = request.args.get('year', '')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT *
            FROM Vehicle
            WHERE 1=1
        """

        params = []

        if make:
            query += " AND vehicle_make LIKE %s"
            params.append(f"%{make}%")

        if model:
            query += " AND vehicle_model LIKE %s"
            params.append(f"%{model}%")

        if year:
            query += " AND vehicle_year = %s"
            params.append(year)

        query += " ORDER BY vehicle_id DESC"

        cursor.execute(query, tuple(params))

        vehicles_data = cursor.fetchall()

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


@vehicle_bp.route('/vehicles/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():

    if request.method == 'POST':

        vehicle_make = request.form['vehicle_make']
        vehicle_model = request.form['vehicle_model']
        vehicle_year = request.form['vehicle_year']
        vehicle_vin = request.form['vehicle_vin']
        vehicle_price = request.form['vehicle_price']
        vehicle_mileage = request.form['vehicle_mileage']
        vehicle_condition = request.form['vehicle_condition']
        vehicle_availability_status = request.form['vehicle_availability_status']

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                INSERT INTO Vehicle
                (
                    vehicle_make,
                    vehicle_model,
                    vehicle_year,
                    vehicle_vin,
                    vehicle_price,
                    vehicle_mileage,
                    vehicle_condition,
                    vehicle_availability_status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(
                query,
                (
                    vehicle_make,
                    vehicle_model,
                    vehicle_year,
                    vehicle_vin,
                    vehicle_price,
                    vehicle_mileage,
                    vehicle_condition,
                    vehicle_availability_status
                )
            )

            conn.commit()

            flash("Vehicle added successfully.", "success")

            return redirect(url_for('vehicle.vehicles'))

        except mysql.connector.Error as err:

            flash(f"MySQL Error: {err}", "error")

        finally:

            if 'cursor' in locals() and cursor is not None:
                cursor.close()

            if 'conn' in locals() and conn is not None and conn.is_connected():
                conn.close()

    return render_template('add_vehicle.html')


@vehicle_bp.route('/vehicles/<int:vehicle_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):

    vehicle = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':

            vehicle_make = request.form['vehicle_make']
            vehicle_model = request.form['vehicle_model']
            vehicle_year = request.form['vehicle_year']
            vehicle_vin = request.form['vehicle_vin']
            vehicle_price = request.form['vehicle_price']
            vehicle_mileage = request.form['vehicle_mileage']
            vehicle_condition = request.form['vehicle_condition']
            vehicle_availability_status = request.form['vehicle_availability_status']

            query = """
                UPDATE Vehicle
                SET
                    vehicle_make = %s,
                    vehicle_model = %s,
                    vehicle_year = %s,
                    vehicle_vin = %s,
                    vehicle_price = %s,
                    vehicle_mileage = %s,
                    vehicle_condition = %s,
                    vehicle_availability_status = %s
                WHERE vehicle_id = %s
            """

            cursor.execute(
                query,
                (
                    vehicle_make,
                    vehicle_model,
                    vehicle_year,
                    vehicle_vin,
                    vehicle_price,
                    vehicle_mileage,
                    vehicle_condition,
                    vehicle_availability_status,
                    vehicle_id
                )
            )

            conn.commit()

            flash("Vehicle updated successfully.", "success")

            return redirect(url_for('vehicle.vehicles'))

        query = """
            SELECT *
            FROM Vehicle
            WHERE vehicle_id = %s
        """

        cursor.execute(query, (vehicle_id,))

        vehicle = cursor.fetchone()

    except mysql.connector.Error as err:

        flash(f"MySQL Error: {err}", "error")

        return redirect(url_for('vehicle.vehicles'))

    finally:

        if 'cursor' in locals() and cursor is not None:
            cursor.close()

        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return render_template(
        'edit_vehicle.html',
        vehicle=vehicle
    )


@vehicle_bp.route('/vehicles/<int:vehicle_id>/delete')
@login_required
def delete_vehicle(vehicle_id):

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check each table that holds a FK reference to Vehicle before deleting.
        # Attempting a blind DELETE will raise a 1451 FK constraint error if any
        # sales, services, or loans reference this vehicle.
        dependency_checks = [
            ("Sale",    "sale_id",    "sale record(s)"),
            ("SERVICE", "service_id", "service record(s)"),
            ("LOAN",    "loan_id",    "loan record(s)"),
        ]

        blocking_refs = []

        for table, id_col, label in dependency_checks:
            cursor.execute(
                f"SELECT COUNT(*) AS cnt FROM {table} WHERE vehicle_id = %s",
                (vehicle_id,)
            )
            row = cursor.fetchone()
            if row and row['cnt'] > 0:
                blocking_refs.append(f"{row['cnt']} {label}")

        if blocking_refs:
            refs_str = ", ".join(blocking_refs)
            flash(
                f"Cannot remove vehicle — it is referenced by: {refs_str}. "
                f"Please resolve those records first.",
                "error"
            )
            return redirect(url_for('vehicle.vehicles'))

        cursor.execute(
            "DELETE FROM Vehicle WHERE vehicle_id = %s",
            (vehicle_id,)
        )

        conn.commit()

        flash("Vehicle removed successfully.", "success")

    except mysql.connector.Error as err:

        flash(f"MySQL Error: {err}", "error")

    finally:

        if 'cursor' in locals() and cursor is not None:
            cursor.close()

        if 'conn' in locals() and conn is not None and conn.is_connected():
            conn.close()

    return redirect(url_for('vehicle.vehicles'))