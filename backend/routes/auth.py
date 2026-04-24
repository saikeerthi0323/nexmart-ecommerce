from flask import Blueprint, request, jsonify, session
import bcrypt
from backend.models.db import get_db

auth_bp = Blueprint('auth', __name__)

# ── HELPER ─────────────────────────────────────────────
def current_user():
    return session.get('user_id')


# ── SIGNUP ─────────────────────────────────────────────
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not name or not email or not password:
        return jsonify(error='All fields are required'), 400

    if len(password) < 6:
        return jsonify(error='Password must be at least 6 characters'), 400

    # hash password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute('SELECT id FROM users WHERE email = %s', (email,))
            if cur.fetchone():
                return jsonify(error='Email already registered'), 409

            cur.execute(
                'INSERT INTO users (name, email, password) VALUES (%s, %s, %s)',
                (name, email, hashed)
            )
            db.commit()
            user_id = cur.lastrowid

        session['user_id'] = user_id
        session['user_role'] = 'user'

        return jsonify(message='Account created')

    except Exception as e:
        db.rollback()
        return jsonify(error=str(e)), 500


# ── LOGIN ─────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
def login():
    data  = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify(error='Email and password required'), 400

    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cur.fetchone()

    # check password
    if not user or not bcrypt.checkpw(password.encode(), user['password'].encode()):
        return jsonify(error='Invalid email or password'), 401

    # 🔥 IMPORTANT: MAKE YOUR EMAIL ADMIN
    if email == "saikeerthi13028@gmail.com":   # 🔁 CHANGE THIS
        role = "admin"
    else:
        role = "user"

    session['user_id'] = user['id']
    session['user_role'] = role

    return jsonify(message='Logged in', user={
        'id': user['id'],
        'name': user['name'],
        'email': user['email'],
        'role': role,
    })


# ── LOGOUT ─────────────────────────────────────────────
@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify(message='Logged out')


# ── CURRENT USER ───────────────────────────────────────
@auth_bp.route('/me', methods=['GET'])
def me():
    uid = current_user()
    if not uid:
        return jsonify(error='Not authenticated'), 401

    db = get_db()
    with db.cursor() as cur:
        cur.execute('SELECT id, name, email FROM users WHERE id = %s', (uid,))
        user = cur.fetchone()

    if not user:
        session.clear()
        return jsonify(error='User not found'), 404

    return jsonify(user=user)