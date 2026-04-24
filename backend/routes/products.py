"""
backend/routes/products.py
===========================
Handles: GET /api/products  /api/products/<id>  search & filter
"""

from flask import Blueprint, request, jsonify
from backend.models.db import get_db

products_bp = Blueprint('products', __name__)


# ── LIST / SEARCH / FILTER ──────────────────────────────────────────────────
@products_bp.route('/', methods=['GET'])
def get_products():
    """
    GET /api/products?search=&category=&min_price=&max_price=&sort=
    Supports full-text search, category filter, price range, and sort.
    """
    search    = request.args.get('search', '').strip()
    category  = request.args.get('category', '').strip()   # category slug
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort      = request.args.get('sort', 'created_at')     # price_asc|price_desc|rating

    # Base query — JOIN with categories to get slug
    sql    = '''SELECT p.*, c.name AS category_name, c.slug AS category_slug
                FROM products p
                JOIN categories c ON p.category_id = c.id
                WHERE 1=1'''
    params = []

    # Dynamic WHERE clauses
    if search:
        sql += ' AND (p.name LIKE %s OR p.description LIKE %s)'
        like = f'%{search}%'
        params += [like, like]

    if category:
        sql += ' AND c.slug = %s'
        params.append(category)

    if min_price is not None:
        sql += ' AND p.price >= %s'
        params.append(min_price)

    if max_price is not None:
        sql += ' AND p.price <= %s'
        params.append(max_price)

    # ORDER BY
    order_map = {
        'price_asc':  'p.price ASC',
        'price_desc': 'p.price DESC',
        'rating':     'p.rating DESC',
        'newest':     'p.created_at DESC',
    }
    sql += f' ORDER BY {order_map.get(sort, "p.created_at DESC")}'

    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, params)
        products = cur.fetchall()

    return jsonify(products=products, count=len(products))


# ── SINGLE PRODUCT ──────────────────────────────────────────────────────────
@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """GET /api/products/<id> — returns one product with category info."""
    db = get_db()
    with db.cursor() as cur:
        cur.execute('''
            SELECT p.*, c.name AS category_name, c.slug AS category_slug
            FROM products p
            JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
        ''', (product_id,))
        product = cur.fetchone()

    if not product:
        return jsonify(error='Product not found'), 404

    return jsonify(product=product)


# ── CATEGORIES LIST ─────────────────────────────────────────────────────────
@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """GET /api/products/categories — list all categories with product counts."""
    db = get_db()
    with db.cursor() as cur:
        cur.execute('''
            SELECT c.*, COUNT(p.id) AS product_count
            FROM categories c
            LEFT JOIN products p ON p.category_id = c.id
            GROUP BY c.id
        ''')
        cats = cur.fetchall()
    return jsonify(categories=cats)
