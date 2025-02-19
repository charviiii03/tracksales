from flask import redirect, url_for, flash
from flask_login import current_user
from functools import wraps
from contextlib import contextmanager
import mysql.connector
import os

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Sumit@123'),
    'database': os.getenv('DB_NAME', 'sales_db')
}

@contextmanager
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_db_cursor():
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        try:
            yield cursor
            conn.commit()
        finally:
            cursor.close()

# Role-based access control decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function