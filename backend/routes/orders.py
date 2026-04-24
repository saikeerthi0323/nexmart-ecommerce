"""
backend/routes/orders.py
========================
Handles: POST /api/orders (place order)  GET /api/orders (history)
"""

from flask import Blueprint, request, jsonify, session
from backend.models.db import get_db

orders_bp = Blueprint('orders', __name__)


# ── PLACE ORDER ──────────────────────────────────────────────────────────────
@orders_bp.route('/place', methods=['POST'])
def place_order():
    """
    POST /api/orders/place
    1. Reads user's cart
    2. Creates an orders row (header)
    3. Creates order_items rows (line items) — snapshots price at purchase time
    4. Decrements product stock
    5. Clears the cart
    All steps are wrapped in a DB transaction.
    """
    uid = session.get('user_id')
    if not uid:
        return jsonify(error='Login required'), 401

    db = get_db()
    try:
        with db.cursor() as cur:
            # 1. Fetch current cart
            cur.execute('''
                SELECT c.product_id, c.quantity, p.price, p.stock, p.name
                FROM cart c
                JOIN products p ON c.product_id = p.id
                WHERE c.user_id = %s
            ''', (uid,))
            cart_items = cur.fetchall()

            if not cart_items:
                return jsonify(error='Cart is empty'), 400

            # 2. Validate stock for each item
            for item in cart_items:
                if item['stock'] < item['quantity']:
                    return jsonify(error=f"Insufficient stock for {item['name']}"), 400

            # 3. Calculate total
            total = sum(i['price'] * i['quantity'] for i in cart_items)

            # 4. INSERT into orders table
            cur.execute(
                'INSERT INTO orders (user_id, total_amount) VALUES (%s, %s)',
                (uid, round(total, 2))
            )
            order_id = cur.lastrowid

            # 5. INSERT order_items (one row per product)
            for item in cart_items:
                cur.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                ''', (order_id, item['product_id'], item['quantity'], item['price']))

                # 6. Decrement stock
                cur.execute(
                    'UPDATE products SET stock = stock - %s WHERE id = %s',
                    (item['quantity'], item['product_id'])
                )

            # 7. Clear cart
            cur.execute('DELETE FROM cart WHERE user_id = %s', (uid,))

        db.commit()
        return jsonify(message='Order placed successfully', order_id=order_id), 201

    except Exception as e:
        db.rollback()
        return jsonify(error=str(e)), 500


# ── ORDER HISTORY ─────────────────────────────────────────────────────────────
@orders_bp.route('/', methods=['GET'])
def get_orders():
    """
    GET /api/orders
    Returns full order history for the logged-in user.
    Uses a JOIN across orders → order_items → products.
    """
    uid = session.get('user_id')
    if not uid:
        return jsonify(error='Login required'), 401

    db = get_db()
    with db.cursor() as cur:
        # Fetch order headers
        cur.execute('''
            SELECT id, total_amount, status, created_at
            FROM orders
            WHERE user_id = %s
            ORDER BY created_at DESC
        ''', (uid,))
        orders = cur.fetchall()

        # Attach line items to each order
        for order in orders:
            cur.execute('''
                SELECT oi.quantity, oi.unit_price,
                       p.name, p.image_url
                FROM order_items oi
                JOIN products p ON oi.product_id = p.id
                WHERE oi.order_id = %s
            ''', (order['id'],))
            order['items'] = cur.fetchall()

    return jsonify(orders=orders)


# ── SINGLE ORDER ──────────────────────────────────────────────────────────────
@orders_bp.route('/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """GET /api/orders/<id> — returns one order with items."""
    uid = session.get('user_id')
    if not uid:
        return jsonify(error='Login required'), 401

    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT * FROM orders WHERE id = %s AND user_id = %s', (order_id, uid))
        order = cur.fetchone()
        if not order:
            return jsonify(error='Order not found'), 404

        cur.execute('''
            SELECT oi.*, p.name, p.image_url
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        ''', (order_id,))
        order['items'] = cur.fetchall()

    return jsonify(order=order)
