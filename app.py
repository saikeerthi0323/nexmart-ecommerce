"""
NEXMART — Flask Backend
=======================
Entry point. Initialises Flask, registers blueprints, and runs the dev server.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from backend.routes.auth    import auth_bp
from backend.routes.products import products_bp
from backend.routes.cart    import cart_bp
from backend.routes.orders  import orders_bp
from backend.routes.admin   import admin_bp
from backend.models.db      import init_db

app = Flask(__name__, static_folder='frontend/static', template_folder='frontend/templates')

# ── Security ──────────────────────────────────────────────────────────────────
app.secret_key = 'nexmart-super-secret-key-change-in-prod'

# ── CORS (allow the frontend to talk to the API) ──────────────────────────────
CORS(app, supports_credentials=True)

# ── Register Blueprints (modular routes) ──────────────────────────────────────
app.register_blueprint(auth_bp,     url_prefix='/api/auth')
app.register_blueprint(products_bp, url_prefix='/api/products')
app.register_blueprint(cart_bp,     url_prefix='/api/cart')
app.register_blueprint(orders_bp,   url_prefix='/api/orders')
app.register_blueprint(admin_bp,    url_prefix='/api/admin')

# ── Serve the SPA for any non-API route ───────────────────────────────────────
from flask import send_from_directory
import os

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.template_folder, 'index.html')

# ── Health check ──────────────────────────────────────────────────────────────
@app.route('/api/health')
def health():
    return jsonify(status='ok', message='NEXMART API running')
if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='127.0.0.1', port=5001)