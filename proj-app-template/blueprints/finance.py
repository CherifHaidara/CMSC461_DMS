from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils import get_db_connection, login_required

finance_bp = Blueprint('finance', __name__)


@finance_bp.route('/loans')
@login_required
def loans():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT l.*, c.customer_name, v.vehicle_make, v.vehicle_model
        FROM LOAN l
        JOIN Customer c ON l.customer_id = c.customer_id
        JOIN Vehicle v ON l.vehicle_id = v.vehicle_id
    """)
    loans = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('loans.html', loans=loans)


@finance_bp.route('/loans/create', methods=['GET', 'POST'])
@login_required
def create_loan():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        customer_id = request.form['customer_id']
        vehicle_id = request.form['vehicle_id']
        loan_amount = request.form['loan_amount']
        interest_rate = request.form['interest_rate']
        loan_term = request.form['loan_term']
        monthly_payment = request.form['monthly_payment']

        cursor.execute("""
            INSERT INTO LOAN (customer_id, vehicle_id, loan_amount, interest_rate, loan_term, monthly_payment, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'pending')
        """, (customer_id, vehicle_id, loan_amount, interest_rate, loan_term, monthly_payment))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Loan created successfully.", "success")
        return redirect(url_for('finance.loans'))

    cursor.execute("SELECT customer_id, customer_name FROM Customer")
    customers = cursor.fetchall()
    cursor.execute("SELECT vehicle_id, vehicle_make, vehicle_model FROM Vehicle WHERE vehicle_availability_status = 'available'")
    vehicles = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('create_loan.html', customers=customers, vehicles=vehicles)


@finance_bp.route('/loans/<int:loan_id>')
@login_required
def loan_detail(loan_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT l.*, c.customer_name, v.vehicle_make, v.vehicle_model
        FROM LOAN l
        JOIN Customer c ON l.customer_id = c.customer_id
        JOIN Vehicle v ON l.vehicle_id = v.vehicle_id
        WHERE l.loan_id = %s
    """, (loan_id,))
    loan = cursor.fetchone()

    cursor.execute("SELECT * FROM LOAN_PAYMENT WHERE loan_id = %s ORDER BY payment_date DESC", (loan_id,))
    payments = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('loan_detail.html', loan=loan, payments=payments)


@finance_bp.route('/loans/<int:loan_id>/payment', methods=['GET', 'POST'])
@login_required
def add_payment(loan_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        amount = request.form['amount']
        payment_date = request.form['payment_date']
        cursor.execute("""
            INSERT INTO LOAN_PAYMENT (loan_id, amount, payment_date)
            VALUES (%s, %s, %s)
        """, (loan_id, amount, payment_date))
        conn.commit()
        cursor.close()
        conn.close()
        flash("Payment recorded successfully.", "success")
        return redirect(url_for('finance.loan_detail', loan_id=loan_id))

    cursor.execute("SELECT * FROM LOAN WHERE loan_id = %s", (loan_id,))
    loan = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('add_payment.html', loan=loan)


@finance_bp.route('/reports')
@login_required
def reports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_sold FROM Sale")
    total_sold = cursor.fetchone()['total_sold']

    cursor.execute("""
        SELECT d.department_name, COUNT(s.sale_id) AS total_sales, SUM(s.sale_price) AS revenue
        FROM Sale s
        JOIN DEPARTMENT d ON s.department_id = d.department_id
        GROUP BY d.department_name
    """)
    sales_by_dept = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) AS total_services, SUM(service_cost) AS service_revenue FROM SERVICE")
    service_stats = cursor.fetchone()

    cursor.execute("SELECT status, COUNT(*) AS total FROM LOAN GROUP BY status")
    loan_summary = cursor.fetchall()

    cursor.execute("""
        SELECT c.customer_name, l.loan_amount,
               COALESCE(SUM(p.amount), 0) AS total_paid,
               l.loan_amount - COALESCE(SUM(p.amount), 0) AS balance
        FROM LOAN l
        JOIN Customer c ON l.customer_id = c.customer_id
        LEFT JOIN LOAN_PAYMENT p ON l.loan_id = p.loan_id
        GROUP BY l.loan_id, c.customer_name, l.loan_amount
    """)
    balances = cursor.fetchall()

    cursor.close()
    conn.close()
    return render_template('reports.html',
        total_sold=total_sold,
        sales_by_dept=sales_by_dept,
        service_stats=service_stats,
        loan_summary=loan_summary,
        balances=balances
    )


@finance_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '')
    filter_type = request.args.get('type', 'customer')
    results = []

    if query:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if filter_type == 'customer':
            cursor.execute("SELECT * FROM Customer WHERE customer_name LIKE %s", (f'%{query}%',))
        elif filter_type == 'vehicle':
            cursor.execute("SELECT * FROM Vehicle WHERE vehicle_make LIKE %s OR vehicle_model LIKE %s OR vehicle_vin LIKE %s",
                           (f'%{query}%', f'%{query}%', f'%{query}%'))
        elif filter_type == 'sale':
            cursor.execute("""
                SELECT s.*, c.customer_name, v.vehicle_make, v.vehicle_model
                FROM Sale s
                JOIN Customer c ON s.customer_id = c.customer_id
                JOIN Vehicle v ON s.vehicle_id = v.vehicle_id
                WHERE c.customer_name LIKE %s OR v.vehicle_model LIKE %s
            """, (f'%{query}%', f'%{query}%'))
        elif filter_type == 'loan':
            cursor.execute("""
                SELECT l.*, c.customer_name
                FROM LOAN l
                JOIN Customer c ON l.customer_id = c.customer_id
                WHERE c.customer_name LIKE %s
            """, (f'%{query}%',))
        elif filter_type == 'service':
            cursor.execute("""
                SELECT sv.*, c.customer_name, v.vehicle_make, v.vehicle_model
                FROM SERVICE sv
                JOIN Customer c ON sv.customer_id = c.customer_id
                JOIN Vehicle v ON sv.vehicle_id = v.vehicle_id
                WHERE c.customer_name LIKE %s OR v.vehicle_model LIKE %s OR sv.service_type LIKE %s
            """, (f'%{query}%', f'%{query}%', f'%{query}%'))

        results = cursor.fetchall()
        cursor.close()
        conn.close()

    return render_template('search.html', results=results, query=query, filter_type=filter_type)
