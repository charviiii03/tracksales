from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from utils import get_db_cursor, admin_required
import os
products = Blueprint('products', __name__)

@products.route('/products')
@login_required
def list_products():
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM products ORDER BY name')
        products = cursor.fetchall()
    return render_template('products/list.html', products=products)

@products.route('/products/create', methods=['GET', 'POST'])
@login_required
def create_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        
        with get_db_cursor() as cursor:
            cursor.execute(
                'INSERT INTO products (name, description, price, stock) VALUES (%s, %s, %s, %s)',
                (name, description, price, stock)
            )
            flash('Product created successfully!', 'success')
            return redirect(url_for('products.list_products'))
    
    return render_template('products/form.html')

@products.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    with get_db_cursor() as cursor:
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            price = float(request.form['price'])
            stock = int(request.form['stock'])
            
            cursor.execute(
                'UPDATE products SET name = %s, description = %s, price = %s, stock = %s WHERE id = %s',
                (name, description, price, stock, id)
            )
            flash('Product updated successfully!', 'success')
            return redirect(url_for('products.list_products'))
        
        cursor.execute('SELECT * FROM products WHERE id = %s', (id,))
        product = cursor.fetchone()
        if not product:
            flash('Product not found!', 'error')
            return redirect(url_for('products.list_products'))
        
        return render_template('products/form.html', product=product)

@products.route('/products/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(id):
    with get_db_cursor() as cursor:
        cursor.execute('DELETE FROM products WHERE id = %s', (id,))
        flash('Product deleted successfully!', 'success')
    return redirect(url_for('products.list_products'))