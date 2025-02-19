from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils import get_db_cursor
from flask_login import login_required, current_user
from datetime import datetime

sales = Blueprint('sales', __name__)

@sales.route('/sales')
@login_required
def list_sales():
    sale_date = request.args.get('sale_date')
    
    with get_db_cursor() as cursor:
        if sale_date:
            cursor.execute("""
                SELECT s.id, c.name as customer_name, s.sale_date, s.total_amount, u.username as created_by
                FROM sales s
                JOIN customers c ON s.customer_id = c.id
                JOIN users u ON s.user_id = u.id
                WHERE DATE(s.sale_date) = %s
                ORDER BY s.sale_date DESC
            """, (sale_date,))
        else:
            cursor.execute("""
                SELECT s.id, c.name as customer_name, s.sale_date, s.total_amount, u.username as created_by
                FROM sales s
                JOIN customers c ON s.customer_id = c.id
                JOIN users u ON s.user_id = u.id
                ORDER BY s.sale_date DESC
            """)
        sales = cursor.fetchall()
    return render_template('sales/list.html', sales=sales)

@sales.route('/sales/create', methods=['GET', 'POST'])
@login_required
def create_sale():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        products = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')
        sale_date = datetime.strptime(request.form['sale_date'], '%Y-%m-%dT%H:%M')

        with get_db_cursor() as cursor:
            try:
                # Create the sale record
                cursor.execute('INSERT INTO sales (customer_id, sale_date, total_amount, user_id) VALUES (%s, %s, %s, %s)', 
                              (customer_id, sale_date, 0, current_user.id))
                sale_id = cursor.lastrowid

                total_amount = 0
                # Add sale items and update product stock
                for product_id, quantity in zip(products, quantities):
                    if not product_id or not quantity:
                        continue
                        
                    quantity = int(quantity)
                    if quantity <= 0:
                        continue

                    # Get product price and current stock
                    cursor.execute('SELECT price, stock FROM products WHERE id = %s', (product_id,))
                    product = cursor.fetchone()
                    if not product or product['stock'] < quantity:
                        raise Exception(f'Insufficient stock for product {product_id}')

                    # Calculate item total
                    item_total = product['price'] * quantity
                    total_amount += item_total

                    # Add sale item
                    cursor.execute('INSERT INTO sale_items (sale_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)',
                                (sale_id, product_id, quantity, product['price']))

                    # Update product stock
                    cursor.execute('UPDATE products SET stock = stock - %s WHERE id = %s',
                                (quantity, product_id))

                # Update sale total
                cursor.execute('UPDATE sales SET total_amount = %s WHERE id = %s',
                            (total_amount, sale_id))

                flash('Sale created successfully!', 'success')
                return redirect(url_for('sales.list_sales'))

            except Exception as e:
                flash(str(e), 'danger')
                return redirect(url_for('sales.create_sale'))

    # Get customers and products for the form
    with get_db_cursor() as cursor:
        cursor.execute('SELECT id, name FROM customers ORDER BY name')
        customers = cursor.fetchall()
        cursor.execute('SELECT id, name, price, stock FROM products WHERE stock > 0 ORDER BY name')
        products = cursor.fetchall()

    return render_template('sales/form.html', customers=customers, products=products)

@sales.route('/sales/<int:id>')
@login_required
def view_sale(id):
    with get_db_cursor() as cursor:
        # Get sale details
        cursor.execute("""
            SELECT s.*, c.name as customer_name
            FROM sales s
            JOIN customers c ON s.customer_id = c.id
            WHERE s.id = %s
        """, (id,))
        sale = cursor.fetchone()

        if sale:
            # Get sale items
            cursor.execute("""
                SELECT si.*, p.name as product_name
                FROM sale_items si
                JOIN products p ON si.product_id = p.id
                WHERE si.sale_id = %s
            """, (id,))
            items = cursor.fetchall()
        else:
            items = []

    if not sale:
        flash('Sale not found.', 'danger')
        return redirect(url_for('sales.list_sales'))

    return render_template('sales/view.html', sale=sale, items=items)

@sales.route('/sales/<int:id>/delete', methods=['POST'])
@login_required
def delete_sale(id):
    if current_user.username != 'pravit':
        flash('Only user pravit can delete sales.', 'danger')
        return redirect(url_for('sales.list_sales'))

    with get_db_cursor() as cursor:
        # Start a transaction
        cursor.execute('BEGIN')
        try:
            # Get sale items to restore product stock
            cursor.execute('SELECT product_id, quantity FROM sale_items WHERE sale_id = %s', (id,))
            items = cursor.fetchall()

            # Restore product stock
            for item in items:
                cursor.execute('UPDATE products SET stock = stock + %s WHERE id = %s',
                            (item['quantity'], item['product_id']))

            # Delete sale items and sale
            cursor.execute('DELETE FROM sale_items WHERE sale_id = %s', (id,))
            cursor.execute('DELETE FROM sales WHERE id = %s', (id,))

            cursor.execute('COMMIT')
            flash('Sale deleted successfully!', 'success')

        except Exception as e:
            cursor.execute('ROLLBACK')
            flash(str(e), 'danger')
    return redirect(url_for('sales.list_sales'))