from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils import get_db_cursor
from flask_login import login_required, current_user

customers = Blueprint('customers', __name__)

@customers.route('/customers')
@login_required
def list_customers():
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM customers ORDER BY name')
        customers = cursor.fetchall()
    return render_template('customers/list.html', customers=customers)

@customers.route('/customers/create', methods=['GET', 'POST'])
@login_required
def create_customer():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        with get_db_cursor() as cursor:
            cursor.execute('INSERT INTO customers (name, email, phone, address) VALUES (%s, %s, %s, %s)',
                        (name, email, phone, address))
            flash('Customer created successfully!', 'success')
            return redirect(url_for('customers.list_customers'))

    return render_template('customers/form.html')

@customers.route('/customers/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_customer(id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        with get_db_cursor() as cursor:
            cursor.execute('UPDATE customers SET name = %s, email = %s, phone = %s, address = %s WHERE id = %s',
                        (name, email, phone, address, id))
            flash('Customer updated successfully!', 'success')
            return redirect(url_for('customers.list_customers'))

    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM customers WHERE id = %s', (id,))
        customer = cursor.fetchone()

    return render_template('customers/form.html', customer=customer)

@customers.route('/customers/<int:id>/delete', methods=['POST'])
@login_required
def delete_customer(id):
    if current_user.role != 'admin':
        flash('Only administrators can delete customers.', 'danger')
        return redirect(url_for('customers.list_customers'))

    with get_db_cursor() as cursor:
        cursor.execute('DELETE FROM customers WHERE id = %s', (id,))
        flash('Customer deleted successfully!', 'success')
    return redirect(url_for('customers.list_customers'))