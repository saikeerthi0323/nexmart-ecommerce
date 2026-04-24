"""
backend/routes/cart.py
======================
Handles: GET/POST/PUT/DELETE /api/cart
All endpoints require authentication.
"""

from flask import Blueprint, request, jsonify, session
from backend.models.db import get_db

cart_bp = Blueprint('cart', __name__)


def require_auth():
    uid = session.get('user_id')
    if not uid:
        return None, jsonify(error='Login required'), 401
    return uid, None, None


# ── GET CART ─────────────────────────────────────────────────────────────────
@cart_bp.route('/', methods=['GET'])
def get_cart():
    """
    GET /api/cart
    Returns all cart items for the logged-in user with product details.
    SQL: SELECT with JOIN on products to pull name, price, image.
    """
    uid = session.get('user_id')
    if not uid:
        return jsonify(error='Login required'), 401

    db = get_db()
    with db.cursor() as cur:
        cur.execute('''
            SELECT c.id AS cart_id, c.quantity,
                   p.id AS product_id, p.name, p.price, p.image_url, p.stock
            FROM cart c
            JOIN products p ON c.product_id = p.id
            WHERE c.user_id = %s
        ''', (uid,))
        items = cur.fetchall()

    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in items)
    return jsonify(items=items, total=round(total, 2))


# ── ADD TO CART ───────────────────────────────────────────────────────────────
@cart_bp.route('/add', methods=['POST'])
def add_to_cart():
    """
    POST /api/cart/add
    Body: { product_id, quantity }
    Uses INSERT ... ON DUPLICATE KEY UPDATE to handle re-adds gracefully.
    """
    uid = session.get('user_id')
    if not uid:
        return jsonify(error='Login required'), 401

    data       = request.get_json()
    product_id = data.get('product_id')
    quantity   = int(data.get('quantity', 1))

    if not product_id or quantity < 1:
        return jsonify(error='Invalid product or quantity'), 400

    db = get_db()
    try:
        with db.cursor() as cur:
            # Verify product exists and has stock
            cur.execute('SELECT stock FROM products WHERE id = %s', (product_id,))
            product = cur.fetchone()
            if not product:
                return jsonify(error='Product not found'), 404
            if product['stock'] < quantity:
                return jsonify(error='Insufficient stock'), 400

            # INSERT or UPDATE quantity (UPSERT pattern)
            cur.execute('''
                INSERT INTO cart (user_id, product_id, quantity)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity)
            ''', (uid, product_id, quantity))
        db.commit()
        return jsonify(message='Added to cart'), 201
    except Exception as e:
        db.rollback()
        return jsonify(error=str(e)), 500


# ── UPDATE QUANTITY ───────────────────────────────────────────────────────────
@cart_bp.route('/update', methods=['PUT'])
def update_cart():
    """
    PUT /api/cart/update
    Body: { cart_id, quantity }
    If quantity == 0, item is removed.
    """
    uid = session.get('user_id')
    if not uid:
        return jsonify(error='Login required'), 401

    data     = request.get_json()
    cart_id  = data.get('cart_id')
    quantity = int(data.get('quantity', 1))

    db = get_db()
    try:
        with db.cursor() as cur:
            if quantity <= 0:
                # DELETE when quantity reaches 0
                cur.execute('DELETE FROM cart WHERE id = %s AND user_id = %s', (cart_id, uid))
            else:
                # UPDATE quantity
                cur.execute(
                    'UPDATE cart SET quantity = %s WHERE id = %s AND user_id = %s',
                    (quantity, cart_id, uid)
                )
        db.commit()
        return jsonify(message='Cart updated')
    except Exception as e:
        db.rollback()
        return jsonify(error=str(e)), 500


# ── REMOVE ITEM ───────────────────────────────────────────────────────────────
@cart_bp.route('/remove/<int:cart_id>', methods=['DELETE'])
def remove_from_cart(cart_id):
    """DELETE /api/cart/remove/<cart_id> — removes one item from cart."""
    uid = session.get('user_id')
    if not uid:
        return jsonify(error='Login required'), 401

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute('DELETE FROM cart WHERE id = %s AND user_id = %s', (cart_id, uid))
        db.commit()
        return jsonify(message='Item removed')
    except Exception as e:
        db.rollback()
        return jsonify(error=str(e)), 500


# ── CLEAR CART ────────────────────────────────────────────────────────────────
@cart_bp.route('/clear', methods=['DELETE'])
def clear_cart():
    """DELETE /api/cart/clear — empties entire cart (called after order placed)."""
    uid = session.get('user_id')
    if not uid:
        return jsonify(error='Login required'), 401

    db = get_db()
    with db.cursor() as cur:
        cur.execute('DELETE FROM cart WHERE user_id = %s', (uid,))
    db.commit()
    return jsonify(message='Cart cleared')
