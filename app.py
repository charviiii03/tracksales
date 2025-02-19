from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from passlib.hash import sha256_crypt
from datetime import datetime
from dotenv import load_dotenv
from utils import get_db_cursor, admin_required
from routes.products import products
from routes.customers import customers
from routes.sales import sales
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Register blueprints
app.register_blueprint(products)
app.register_blueprint(customers)
app.register_blueprint(sales)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.role = user_data['role']

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user_data = cursor.fetchone()
        return User(user_data) if user_data else None

# Basic routes
@app.route('/')
def index():
    return redirect(url_for('login'))

# Track failed login attempts
failed_attempts = {}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with get_db_cursor() as cursor:
            cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
            user_data = cursor.fetchone()

            if user_data and sha256_crypt.verify(password, user_data['password_hash']):
                user = User(user_data)
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    with get_db_cursor() as cursor:
        # Get total sales count
        cursor.execute('SELECT COUNT(*) as count FROM sales')
        total_sales = cursor.fetchone()['count']
        
        # Get total customers
        cursor.execute('SELECT COUNT(*) as count FROM customers')
        total_customers = cursor.fetchone()['count']
        
        # Get total products
        cursor.execute('SELECT COUNT(*) as count FROM products')
        total_products = cursor.fetchone()['count']
        
        # Get today's sales
        cursor.execute('SELECT COALESCE(SUM(total_amount), 0) as total FROM sales WHERE DATE(sale_date) = CURDATE()')
        today_sales = cursor.fetchone()['total']
        
        # Get recent sales
        cursor.execute('''
            SELECT s.id, c.name as customer_name, s.total_amount, s.sale_date 
            FROM sales s 
            JOIN customers c ON s.customer_id = c.id 
            ORDER BY s.sale_date DESC LIMIT 5
        ''')
        recent_sales = cursor.fetchall()
        
        # Get low stock products (less than 10 items)
        cursor.execute('SELECT * FROM products WHERE stock < 10 ORDER BY stock ASC LIMIT 5')
        low_stock_products = cursor.fetchall()
    
    return render_template('dashboard.html',
                          total_sales=total_sales,
                          total_customers=total_customers,
                          total_products=total_products,
                          today_sales=today_sales,
                          recent_sales=recent_sales,
                          low_stock_products=low_stock_products)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('register.html')

        with get_db_cursor() as cursor:
            # Check if username already exists
            cursor.execute('SELECT id FROM users WHERE username = %s', (username,))
            if cursor.fetchone():
                flash('Username already exists', 'danger')
                return render_template('register.html')

            # Hash the password and create the user
            password_hash = sha256_crypt.hash(password)
            cursor.execute(
                'INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)',
                (username, password_hash, 'salesperson')
            )
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)