"""
backend/routes/admin.py
=======================
Admin-only CRUD for products.
All routes check session role == 'admin'.
"""

from flask import Blueprint, request, jsonify, session
from backend.models.db import get_db

admin_bp = Blueprint('admin', __name__)


def require_admin():
    """Returns (uid, None) if admin, or (None, error_response) if not."""
    uid  = session.get('user_id')
    role = session.get('user_role')
    if not uid or role != 'admin':
        return None, (jsonify(error='Admin access required'), 403)
    return uid, None


# ── GET ALL PRODUCTS (admin view includes stock) ──────────────────────────────
@admin_bp.route('/products', methods=['GET'])
def admin_get_products():
    uid, err = require_admin()
    if err: return err

    db = get_db()
    with db.cursor() as cur:
        cur.execute('''
            SELECT p.*, c.name AS category_name
            FROM products p
            JOIN categories c ON p.category_id = c.id
            ORDER BY p.created_at DESC
        ''')
        products = cur.fetchall()
    return jsonify(products=products)


# ── ADD PRODUCT ───────────────────────────────────────────────────────────────
@admin_bp.route('/products', methods=['POST'])
def add_product():
    """
    POST /api/admin/products
    Body: { category_id, name, description, price, image_url, stock }
    """
    uid, err = require_admin()
    if err: return err

    data = request.get_json()
    required = ['category_id', 'name', 'price']
    for field in required:
        if not data.get(field):
            return jsonify(error=f'{field} is required'), 400

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute('''
                INSERT INTO products (category_id, name, description, price, image_url, stock)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                data['category_id'],
                data['name'],
                data.get('description', ''),
                float(data['price']),
                data.get('image_url', ''),
                int(data.get('stock', 0)),
            ))
        db.commit()
        return jsonify(message='Product added', id=cur.lastrowid), 201
    except Exception as e:
        db.rollback()
        return jsonify(error=str(e)), 500


# ── EDIT PRODUCT ──────────────────────────────────────────────────────────────
@admin_bp.route('/products/<int:product_id>', methods=['PUT'])
def edit_product(product_id):
    """PUT /api/admin/products/<id> — updates any subset of fields."""
    uid, err = require_admin()
    if err: return err

    data = request.get_json()
    fields = []
    values = []

    # Build dynamic SET clause from whichever fields are provided
    for col in ['category_id', 'name', 'description', 'price', 'image_url', 'stock', 'rating']:
        if col in data:
            fields.append(f'{col} = %s')
            values.append(data[col])

    if not fields:
        return jsonify(error='No fields to update'), 400

    values.append(product_id)
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute(f'UPDATE products SET {", ".join(fields)} WHERE id = %s', values)
        db.commit()
        return jsonify(message='Product updated')
    except Exception as e:
        db.rollback()
        return jsonify(error=str(e)), 500


# ── DELETE PRODUCT ────────────────────────────────────────────────────────────
@admin_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """DELETE /api/admin/products/<id>."""
    uid, err = require_admin()
    if err: return err

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute('DELETE FROM products WHERE id = %s', (product_id,))
        db.commit()
        return jsonify(message='Product deleted')
    except Exception as e:
        db.rollback()
        return jsonify(error=str(e)), 500


# ── ALL ORDERS (admin dashboard) ──────────────────────────────────────────────
@admin_bp.route('/orders', methods=['GET'])
def admin_orders():
    uid, err = require_admin()
    if err: return err

    db = get_db()
    with db.cursor() as cur:
        cur.execute('''
            SELECT o.id, o.total_amount, o.status, o.created_at,
                   u.name AS user_name, u.email
            FROM orders o
            JOIN users u ON o.user_id = u.id
            ORDER BY o.created_at DESC
            LIMIT 100
        ''')
        orders = cur.fetchall()
    return jsonify(orders=orders)


# ── UPDATE ORDER STATUS ───────────────────────────────────────────────────────
@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    uid, err = require_admin()
    if err: return err

    status = request.get_json().get('status')
    valid  = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
    if status not in valid:
        return jsonify(error='Invalid status'), 400

    db = get_db()
    with db.cursor() as cur:
        cur.execute('UPDATE orders SET status = %s WHERE id = %s', (status, order_id))
    db.commit()
    return jsonify(message='Status updated')


# ── DASHBOARD STATS ───────────────────────────────────────────────────────────
@admin_bp.route('/stats', methods=['GET'])
def stats():
    uid, err = require_admin()
    if err: return err

    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT COUNT(*) AS cnt FROM users WHERE role = "user"')
        users = cur.fetchone()['cnt']

        cur.execute('SELECT COUNT(*) AS cnt FROM products')
        products = cur.fetchone()['cnt']

        cur.execute('SELECT COUNT(*) AS cnt FROM orders')
        orders = cur.fetchone()['cnt']

        cur.execute('SELECT COALESCE(SUM(total_amount), 0) AS rev FROM orders WHERE status != "cancelled"')
        revenue = cur.fetchone()['rev']

    return jsonify(users=users, products=products, orders=orders, revenue=float(revenue))
