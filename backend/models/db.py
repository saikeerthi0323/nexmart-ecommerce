"""
backend/models/db.py
====================
Database connection pool using PyMySQL.
All routes import `get_db()` to get a cursor.
"""

import pymysql
import pymysql.cursors
from flask import g, current_app

# ── Connection config — override with env vars in production ──────────────────
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'Keerthi@143',          # set your MySQL password here
    'database': 'nexmart',
    'charset':  'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,  # rows as dicts, not tuples
    'autocommit': False,
}


def get_connection():
    """Open a new MySQL connection."""
    return pymysql.connect(**DB_CONFIG)


def get_db():
    """
    Return the per-request DB connection stored in Flask's 'g' proxy.
    Creates a new connection on first call within a request.
    """
    if 'db' not in g:
        g.db = get_connection()
    return g.db


def close_db(e=None):
    """Close DB connection at end of each request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """
    Read schema.sql and execute it to create all tables.
    Safe to call on every startup (uses CREATE TABLE IF NOT EXISTS).
    """
    import os
    schema_path = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'schema.sql')
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            with open(schema_path, 'r') as f:
                # Execute each statement individually
                statements = [s.strip() for s in f.read().split(';') if s.strip()]
                for stmt in statements:
                    try:
                        cur.execute(stmt)
                    except Exception:
                        pass   # table already exists etc.
        conn.commit()
        print('[DB] Schema initialised successfully.')
    finally:
        conn.close()
