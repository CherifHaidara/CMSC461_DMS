# utils.py
from functools import wraps
from flask import session, flash, redirect, url_for
import mysql.connector
import math

def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="my-secret-pw",
        database="car_dealership",
        port=3306
    )

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to be logged in to view this page.", "error")
            # Note the "auth." prefix! We'll explain this in Step 4.
            return redirect(url_for('auth.login')) 
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to be logged in to view this page.", "error")
            return redirect(url_for('auth.login'))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT role_id FROM `USER` WHERE user_id=%s", (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user or user['role_id'] != 1:  # role_id 1 is Administrator
            flash("You do not have permission to access this page.", "error")
            return redirect(url_for('dashboard.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def build_pagination(*, page: int, total_items: int, per_page: int = 10) -> dict:
    """Create pagination metadata for LIMIT/OFFSET queries."""
    if per_page <= 0:
        per_page = 10

    total_pages = max(1, math.ceil(max(0, total_items) / per_page))
    page = max(1, min(int(page or 1), total_pages))
    offset = (page - 1) * per_page

    return {
        "page": page,
        "per_page": per_page,
        "total_items": total_items,
        "total_pages": total_pages,
        "offset": offset,
        "has_prev": page > 1,
        "has_next": page < total_pages,
        "prev_page": page - 1,
        "next_page": page + 1,
        "start_index": offset + 1 if total_items else 0,
        "end_index": min(offset + per_page, total_items) if total_items else 0,
    }