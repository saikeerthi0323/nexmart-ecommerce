-- ============================================================
-- NEXMART — Sample SQL Queries (Interview Reference)
-- ============================================================

USE nexmart;

-- ─────────────────────────────────────────────────────────────
-- SELECT Queries
-- ─────────────────────────────────────────────────────────────

-- 1. All products with category name (INNER JOIN)
SELECT p.id, p.name, c.name AS category, p.price, p.stock, p.rating
FROM products p
INNER JOIN categories c ON p.category_id = c.id
ORDER BY p.created_at DESC;

-- 2. Search products by keyword (LIKE wildcard)
SELECT p.*, c.name AS category
FROM products p
JOIN categories c ON p.category_id = c.id
WHERE p.name LIKE '%shirt%' OR p.description LIKE '%shirt%';

-- 3. Filter by category + price range
SELECT p.name, p.price, p.rating
FROM products p
JOIN categories c ON p.category_id = c.id
WHERE c.slug = 'electronics'
  AND p.price BETWEEN 100 AND 500
ORDER BY p.price ASC;

-- 4. User cart with product details
SELECT c.id AS cart_id, c.quantity,
       p.name, p.price,
       (c.quantity * p.price) AS line_total
FROM cart c
JOIN products p ON c.product_id = p.id
WHERE c.user_id = 1;

-- 5. Order history with line items (3-table JOIN)
SELECT o.id AS order_id,
       o.created_at,
       o.status,
       o.total_amount,
       p.name AS product,
       oi.quantity,
       oi.unit_price
FROM orders o
JOIN order_items oi  ON oi.order_id   = o.id
JOIN products p      ON oi.product_id = p.id
WHERE o.user_id = 1
ORDER BY o.created_at DESC;

-- 6. Revenue per category (GROUP BY + SUM aggregate)
SELECT c.name AS category,
       COUNT(oi.id) AS items_sold,
       SUM(oi.quantity * oi.unit_price) AS total_revenue
FROM order_items oi
JOIN products p   ON oi.product_id = p.id
JOIN categories c ON p.category_id  = c.id
GROUP BY c.id, c.name
ORDER BY total_revenue DESC;

-- 7. Top 5 best-selling products
SELECT p.name,
       SUM(oi.quantity) AS units_sold
FROM order_items oi
JOIN products p ON oi.product_id = p.id
GROUP BY p.id, p.name
ORDER BY units_sold DESC
LIMIT 5;

-- 8. Users who have never placed an order (LEFT JOIN + IS NULL)
SELECT u.id, u.name, u.email
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE o.id IS NULL;

-- 9. Admin dashboard stats in one query
SELECT
    (SELECT COUNT(*) FROM users  WHERE role = 'user')         AS total_users,
    (SELECT COUNT(*) FROM products)                           AS total_products,
    (SELECT COUNT(*) FROM orders)                             AS total_orders,
    (SELECT COALESCE(SUM(total_amount), 0)
     FROM orders WHERE status != 'cancelled')                 AS total_revenue;


-- ─────────────────────────────────────────────────────────────
-- INSERT Queries
-- ─────────────────────────────────────────────────────────────

-- 10. Register a new user (password must be pre-hashed in Python)
INSERT INTO users (name, email, password)
VALUES ('Jane Doe', 'jane@example.com', '$2b$12$...');

-- 11. Add a new product
INSERT INTO products (category_id, name, description, price, image_url, stock)
VALUES (1, 'Polo Shirt', 'Premium pique cotton polo', 39.99,
        'https://example.com/polo.jpg', 100);

-- 12. Add item to cart (UPSERT — prevents duplicate rows)
INSERT INTO cart (user_id, product_id, quantity)
VALUES (2, 7, 1)
ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity);

-- 13. Create an order header
INSERT INTO orders (user_id, total_amount)
VALUES (2, 149.97);

-- 14. Insert order line item (snapshot price at purchase time)
INSERT INTO order_items (order_id, product_id, quantity, unit_price)
VALUES (LAST_INSERT_ID(), 7, 2, 49.99);


-- ─────────────────────────────────────────────────────────────
-- UPDATE Queries
-- ─────────────────────────────────────────────────────────────

-- 15. Decrement stock when order is placed
UPDATE products
SET stock = stock - 2
WHERE id = 7 AND stock >= 2;   -- guard against negative stock

-- 16. Update cart quantity
UPDATE cart
SET quantity = 3
WHERE user_id = 2 AND product_id = 7;

-- 17. Change order status
UPDATE orders
SET status = 'shipped'
WHERE id = 5;

-- 18. Edit product details (admin)
UPDATE products
SET name = 'Premium Polo Shirt', price = 44.99
WHERE id = 11;


-- ─────────────────────────────────────────────────────────────
-- DELETE Queries
-- ─────────────────────────────────────────────────────────────

-- 19. Remove a specific item from cart
DELETE FROM cart
WHERE user_id = 2 AND product_id = 7;

-- 20. Clear entire cart after order placement
DELETE FROM cart
WHERE user_id = 2;

-- 21. Delete a product (cascades to cart via FK)
DELETE FROM products WHERE id = 11;

-- 22. Cancel and remove an order (cascades to order_items via FK)
DELETE FROM orders WHERE id = 5 AND user_id = 2;


-- ─────────────────────────────────────────────────────────────
-- TRANSACTION Example (Place Order atomically)
-- ─────────────────────────────────────────────────────────────

START TRANSACTION;

    -- Step 1: Create order
    INSERT INTO orders (user_id, total_amount) VALUES (2, 99.98);
    SET @order_id = LAST_INSERT_ID();

    -- Step 2: Insert line item
    INSERT INTO order_items (order_id, product_id, quantity, unit_price)
    VALUES (@order_id, 3, 2, 49.99);

    -- Step 3: Decrement stock
    UPDATE products SET stock = stock - 2 WHERE id = 3;

    -- Step 4: Clear cart
    DELETE FROM cart WHERE user_id = 2;

COMMIT;
-- If any step fails: ROLLBACK;
