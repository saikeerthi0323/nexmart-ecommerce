# NEXMART — Full-Stack eCommerce Application

> A production-quality eCommerce platform built with **Flask**, **MySQL**, and **Vanilla JS** — designed to impress in technical interviews.

---

## 🏗️ Project Structure

```
nexmart/
├── app.py                        # Flask entry point
├── requirements.txt
├── README.md
│
├── backend/
│   ├── models/
│   │   └── db.py                 # MySQL connection pool
│   └── routes/
│       ├── auth.py               # Signup, Login, Logout, /me
│       ├── products.py           # Browse, search, filter
│       ├── cart.py               # Add, update, remove, clear
│       ├── orders.py             # Place order, history
│       └── admin.py              # Admin CRUD + stats
│
├── frontend/
│   ├── templates/
│   │   └── index.html            # Single-page app shell
│   └── static/
│       ├── css/style.css         # Full responsive stylesheet
│       └── js/app.js             # SPA logic (no framework)
│
└── database/
    ├── schema.sql                # CREATE TABLE statements
    └── seed.sql                  # Sample data + query examples
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+
- MySQL 8.0+
- pip

### 2. Clone & Install
```bash
git clone <repo-url>
cd nexmart
pip install -r requirements.txt
```

### 3. MySQL Setup
```sql
-- In MySQL shell:
CREATE DATABASE nexmart;
SOURCE database/schema.sql;
SOURCE database/seed.sql;
```

### 4. Configure DB Password
Edit `backend/models/db.py`:
```python
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': 'YOUR_PASSWORD',   # ← change this
    'database': 'nexmart',
    ...
}
```

### 5. Run
```bash
python app.py
```
Open **http://localhost:5000** in your browser.

---

## 🔑 Test Credentials

| Role  | Email                | Password  |
|-------|----------------------|-----------|
| Admin | admin@nexmart.com    | admin123  |
| User  | *(register via UI)*  | any       |

---

## 🗄️ Database Design

### Entity-Relationship Overview

```
users ──────< orders ──────< order_items >────── products
                                                     │
cart >────────────────────────────────────────────── ┘
                                                     │
categories <─────────────────────────────────────── ┘
```

### Tables

#### `users`
| Column     | Type         | Notes                  |
|------------|--------------|------------------------|
| id         | INT PK AI    | Auto-increment PK      |
| name       | VARCHAR(100) |                        |
| email      | VARCHAR(150) | UNIQUE                 |
| password   | VARCHAR(255) | bcrypt hash            |
| role       | ENUM         | 'user' or 'admin'      |
| created_at | TIMESTAMP    | Default now()          |

#### `categories`
| Column | Type         | Notes       |
|--------|--------------|-------------|
| id     | INT PK AI    |             |
| name   | VARCHAR(100) | UNIQUE      |
| slug   | VARCHAR(100) | URL-friendly|

#### `products`
| Column      | Type          | Notes                      |
|-------------|---------------|----------------------------|
| id          | INT PK AI     |                            |
| category_id | INT FK        | → categories.id CASCADE    |
| name        | VARCHAR(200)  |                            |
| description | TEXT          |                            |
| price       | DECIMAL(10,2) |                            |
| image_url   | VARCHAR(500)  |                            |
| stock       | INT           | Default 0                  |
| rating      | DECIMAL(3,1)  | Default 4.0                |

#### `cart`
| Column     | Type      | Notes                              |
|------------|-----------|------------------------------------|
| id         | INT PK AI |                                    |
| user_id    | INT FK    | → users.id CASCADE                 |
| product_id | INT FK    | → products.id CASCADE              |
| quantity   | INT       |                                    |
| UNIQUE     |           | (user_id, product_id) — no dupes   |

#### `orders`
| Column       | Type          | Notes                     |
|--------------|---------------|---------------------------|
| id           | INT PK AI     |                           |
| user_id      | INT FK        | → users.id CASCADE        |
| total_amount | DECIMAL(10,2) |                           |
| status       | ENUM          | pending/processing/…      |

#### `order_items`
| Column     | Type          | Notes                     |
|------------|---------------|---------------------------|
| id         | INT PK AI     |                           |
| order_id   | INT FK        | → orders.id CASCADE       |
| product_id | INT FK        | → products.id SET NULL    |
| quantity   | INT           |                           |
| unit_price | DECIMAL(10,2) | Snapshot at purchase time |

---

## 🔍 Key SQL Queries (Interview-Ready)

```sql
-- 1. Products with category name
SELECT p.*, c.name AS category
FROM products p
JOIN categories c ON p.category_id = c.id
ORDER BY p.rating DESC;

-- 2. UPSERT — add/increment cart item
INSERT INTO cart (user_id, product_id, quantity) VALUES (1, 5, 2)
ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity);

-- 3. Full order history with line items
SELECT o.id, u.name, p.name AS product,
       oi.quantity, oi.unit_price, o.status
FROM orders o
JOIN users u         ON o.user_id    = u.id
JOIN order_items oi  ON oi.order_id  = o.id
JOIN products p      ON oi.product_id = p.id
WHERE o.user_id = 1
ORDER BY o.created_at DESC;

-- 4. Revenue per category (aggregate + GROUP BY)
SELECT c.name, SUM(oi.quantity * oi.unit_price) AS revenue
FROM order_items oi
JOIN products p   ON oi.product_id = p.id
JOIN categories c ON p.category_id  = c.id
GROUP BY c.name
ORDER BY revenue DESC;

-- 5. Dynamic search with LIKE
SELECT * FROM products
WHERE name LIKE '%shirt%' OR description LIKE '%shirt%';

-- 6. Stock decrement (atomic update in transaction)
UPDATE products SET stock = stock - 2 WHERE id = 5 AND stock >= 2;
```

---

## 🌐 API Reference

| Method | Endpoint                      | Description            | Auth  |
|--------|-------------------------------|------------------------|-------|
| POST   | /api/auth/signup              | Register               | No    |
| POST   | /api/auth/login               | Login                  | No    |
| POST   | /api/auth/logout              | Logout                 | Yes   |
| GET    | /api/auth/me                  | Session check          | Yes   |
| GET    | /api/products/                | List / search / filter | No    |
| GET    | /api/products/:id             | Single product         | No    |
| GET    | /api/products/categories      | All categories         | No    |
| GET    | /api/cart/                    | View cart              | Yes   |
| POST   | /api/cart/add                 | Add to cart            | Yes   |
| PUT    | /api/cart/update              | Update quantity        | Yes   |
| DELETE | /api/cart/remove/:id          | Remove item            | Yes   |
| POST   | /api/orders/place             | Place order            | Yes   |
| GET    | /api/orders/                  | Order history          | Yes   |
| GET    | /api/admin/products           | All products (admin)   | Admin |
| POST   | /api/admin/products           | Add product            | Admin |
| PUT    | /api/admin/products/:id       | Edit product           | Admin |
| DELETE | /api/admin/products/:id       | Delete product         | Admin |
| GET    | /api/admin/stats              | Dashboard stats        | Admin |

---

## 🔒 Security Highlights

- **bcrypt** password hashing (cost factor 12)
- **Server-side sessions** (Flask session, never expose secrets client-side)
- **Role-based access control** (user / admin) on every admin route
- **Foreign key constraints** enforce referential integrity at DB level
- **UPSERT pattern** prevents duplicate cart entries
- **Transaction wrapping** for order placement (atomic: insert order → insert items → decrement stock → clear cart)

---

## 🎨 Features at a Glance

| Feature               | Status |
|-----------------------|--------|
| User Auth (JWT-free)  | ✅     |
| Product Browse        | ✅     |
| Search + Filter       | ✅     |
| Shopping Cart (DB)    | ✅     |
| Place Order           | ✅     |
| Order History         | ✅     |
| Admin Dashboard       | ✅     |
| Admin Product CRUD    | ✅     |
| Mobile Responsive     | ✅     |
| Stock Management      | ✅     |

---

*Built with ❤️ — ready for your next interview!*
