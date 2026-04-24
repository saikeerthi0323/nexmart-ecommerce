-- ============================================================
-- NEXMART eCommerce Database Schema
-- Description: Full schema for Users, Products, Cart, Orders
-- ============================================================

CREATE DATABASE IF NOT EXISTS nexmart;
USE nexmart;

-- -----------------------------------------------------------
-- TABLE: users
-- Stores registered user accounts securely
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100)        NOT NULL,
    email       VARCHAR(150)        NOT NULL UNIQUE,
    password    VARCHAR(255)        NOT NULL,        -- bcrypt hashed
    role        ENUM('user','admin') DEFAULT 'user', -- access control
    created_at  TIMESTAMP           DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------
-- TABLE: categories
-- Product categories (Men, Women, Electronics, etc.)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS categories (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(100) NOT NULL UNIQUE,
    slug  VARCHAR(100) NOT NULL UNIQUE                -- URL-friendly name
);

-- -----------------------------------------------------------
-- TABLE: products
-- All product listings with FK to categories
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    category_id  INT            NOT NULL,
    name         VARCHAR(200)   NOT NULL,
    description  TEXT,
    price        DECIMAL(10,2)  NOT NULL,
    image_url    VARCHAR(500),
    stock        INT            DEFAULT 0,
    rating       DECIMAL(3,1)   DEFAULT 4.0,
    created_at   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- -----------------------------------------------------------
-- TABLE: cart
-- Shopping cart items linked to users and products
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS cart (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT  NOT NULL,
    product_id  INT  NOT NULL,
    quantity    INT  DEFAULT 1,
    added_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)    REFERENCES users(id)    ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    UNIQUE KEY unique_cart_item (user_id, product_id) -- prevent duplicates
);

-- -----------------------------------------------------------
-- TABLE: orders
-- Order headers — one row per placed order
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT            NOT NULL,
    total_amount DECIMAL(10,2)  NOT NULL,
    status       ENUM('pending','processing','shipped','delivered','cancelled')
                                DEFAULT 'pending',
    created_at   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- -----------------------------------------------------------
-- TABLE: order_items
-- Line items for each order (many-to-one with orders)
-- -----------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    order_id    INT            NOT NULL,
    product_id  INT            NOT NULL,
    quantity    INT            NOT NULL,
    unit_price  DECIMAL(10,2)  NOT NULL,  -- snapshot of price at order time
    FOREIGN KEY (order_id)   REFERENCES orders(id)   ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);
