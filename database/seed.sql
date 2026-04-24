-- ============================================================
-- NEXMART Sample Data (Seed File)
-- Run AFTER schema.sql
-- ============================================================

USE nexmart;

-- -----------------------------------------------------------
-- Categories
-- -----------------------------------------------------------
INSERT IGNORE INTO categories (name, slug) VALUES
    ('Men',         'men'),
    ('Women',       'women'),
    ('Electronics', 'electronics'),
    ('Sports',      'sports'),
    ('Home & Living','home-living');

-- -----------------------------------------------------------
-- Admin user  (password = "admin123" bcrypt hash)
-- -----------------------------------------------------------
INSERT IGNORE INTO users (name, email, password, role) VALUES
('Admin User', 'admin@nexmart.com',
 '$2b$12$EIXcYYAWj9bW3YFhHBxOI.5RoEqgz6J0/WV0JV8VvR5DdCMxO4.Da', 'admin');

-- -----------------------------------------------------------
-- Products — Men (category_id = 1)
-- -----------------------------------------------------------
INSERT INTO products (category_id, name, description, price, image_url, stock, rating) VALUES
(1, 'Classic Oxford Shirt',
 'Premium 100% Egyptian cotton Oxford shirt. Timeless button-down collar with a relaxed modern fit. Perfect for office or weekend wear.',
 49.99, 'https://images.unsplash.com/photo-1598033129183-c4f50c736f10?w=600', 85, 4.5),

(1, 'Slim-Fit Chino Pants',
 'Tailored slim-fit chinos in stretch-cotton blend. Five-pocket styling with a clean silhouette. Available in multiple colours.',
 59.99, 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?w=600', 60, 4.3),

(1, 'Leather Derby Shoes',
 'Hand-crafted full-grain leather derby shoes. Cushioned insole and rubber outsole for all-day comfort.',
 129.99, 'https://images.unsplash.com/photo-1533867617858-e7b97e060509?w=600', 40, 4.7),

(1, 'Merino Wool Sweater',
 'Superfine merino wool crew-neck sweater. Naturally temperature-regulating and machine-washable.',
 89.99, 'https://images.unsplash.com/photo-1614975059251-992f11792b9f?w=600', 55, 4.4),

(1, 'Denim Jacket – Indigo',
 'Classic indigo denim jacket with button front and chest pockets. Washed for a lived-in look right out of the box.',
 79.99, 'https://images.unsplash.com/photo-1601333144130-8cbb312386b6?w=600', 70, 4.2);

-- -----------------------------------------------------------
-- Products — Women (category_id = 2)
-- -----------------------------------------------------------
INSERT INTO products (category_id, name, description, price, image_url, stock, rating) VALUES
(2, 'Floral Wrap Dress',
 'Elegant wrap dress in a vibrant floral print. V-neck silhouette with a self-tie waist for a flattering fit.',
 69.99, 'https://images.unsplash.com/photo-1572804013427-4d7ca7268217?w=600', 90, 4.6),

(2, 'High-Rise Skinny Jeans',
 'Premium stretch denim high-rise skinny jeans. Sculpting fit with a comfortable waistband. Classic five-pocket design.',
 74.99, 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600', 100, 4.5),

(2, 'Cashmere Turtleneck',
 'Luxuriously soft Grade-A cashmere turtleneck. Ribbed cuffs and hem. A wardrobe investment piece.',
 149.99, 'https://images.unsplash.com/photo-1576566588028-4147f3842f27?w=600', 30, 4.8),

(2, 'Strappy Block-Heel Sandals',
 'Elegant strappy sandals with a comfortable 7 cm block heel. Adjustable ankle strap. Versatile nude tone.',
 89.99, 'https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600', 50, 4.3),

(2, 'Trench Coat – Camel',
 'Classic double-breasted trench coat in water-resistant camel gabardine. Belt waist with epaulettes.',
 199.99, 'https://images.unsplash.com/photo-1548624313-0396c75e4b1a?w=600', 25, 4.9);

-- -----------------------------------------------------------
-- Products — Electronics (category_id = 3)
-- -----------------------------------------------------------
INSERT INTO products (category_id, name, description, price, image_url, stock, rating) VALUES
(3, 'Wireless Noise-Cancelling Headphones',
 '40-hour battery life, active noise cancellation, Hi-Res Audio certified. Foldable premium build with premium carrying case.',
 249.99, 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600', 45, 4.8),

(3, '4K Ultra HD Smart TV – 55"',
 'Quantum dot display, Dolby Vision IQ & Dolby Atmos, built-in voice assistant. 4 HDMI 2.1 ports.',
 699.99, 'https://images.unsplash.com/photo-1593359677879-a4bb92f829e1?w=600', 20, 4.7),

(3, 'Mechanical Gaming Keyboard',
 'TKL layout with Cherry MX Red switches. Per-key RGB lighting, aluminium top plate, USB-C detachable cable.',
 119.99, 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600', 65, 4.6),

(3, 'True Wireless Earbuds',
 '6-hour playtime + 24h case, IPX4 water resistance, adaptive EQ, transparency mode.',
 99.99, 'https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600', 80, 4.5),

(3, 'Smart Watch – Fitness Pro',
 'Always-on AMOLED display, GPS, SpO2 & ECG sensors, 14-day battery, 100+ workout modes.',
 299.99, 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600', 35, 4.6);

-- -----------------------------------------------------------
-- Products — Sports (category_id = 4)
-- -----------------------------------------------------------
INSERT INTO products (category_id, name, description, price, image_url, stock, rating) VALUES
(4, 'Running Shoes – UltraBoost',
 'Responsive Boost midsole, Primeknit upper, Continental rubber outsole. Ideal for road running.',
 159.99, 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600', 70, 4.7),

(4, 'Yoga Mat – Premium Cork',
 'Natural cork surface for superior grip when wet. 5mm TPE base layer. Alignment lines printed.',
 49.99, 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=600', 120, 4.4);

-- -----------------------------------------------------------
-- Products — Home & Living (category_id = 5)
-- -----------------------------------------------------------
INSERT INTO products (category_id, name, description, price, image_url, stock, rating) VALUES
(5, 'Scented Soy Candle Set',
 'Set of 3 hand-poured soy wax candles: Sandalwood & Cedar, Jasmine & White Tea, Amber & Vanilla. 45 hr burn each.',
 39.99, 'https://images.unsplash.com/photo-1603006905003-be475563bc59?w=600', 200, 4.5),

(5, 'Ceramic Pour-Over Coffee Set',
 'Handcrafted ceramic dripper + carafe + 40 paper filters. Brews 2-4 cups. Dishwasher safe.',
 59.99, 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=600', 60, 4.6);

-- ============================================================
-- SAMPLE SQL QUERIES (for interview demonstration)
-- ============================================================

-- 1. SELECT: Get all products with category name, ordered by price
-- SELECT p.id, p.name, c.name AS category, p.price, p.stock
-- FROM products p
-- JOIN categories c ON p.category_id = c.id
-- ORDER BY p.price DESC;

-- 2. INSERT: Add item to cart
-- INSERT INTO cart (user_id, product_id, quantity)
-- VALUES (1, 3, 2)
-- ON DUPLICATE KEY UPDATE quantity = quantity + 2;

-- 3. UPDATE: Change product stock after order
-- UPDATE products SET stock = stock - 1 WHERE id = 5;

-- 4. DELETE: Remove item from cart
-- DELETE FROM cart WHERE user_id = 1 AND product_id = 3;

-- 5. SELECT with JOIN: Full order history with items
-- SELECT o.id, u.name, p.name AS product, oi.quantity, oi.unit_price, o.status
-- FROM orders o
-- JOIN users u        ON o.user_id    = u.id
-- JOIN order_items oi ON oi.order_id  = o.id
-- JOIN products p     ON oi.product_id = p.id
-- WHERE o.user_id = 1
-- ORDER BY o.created_at DESC;

-- 6. Aggregate: Revenue per category
-- SELECT c.name, COUNT(oi.id) AS items_sold, SUM(oi.quantity * oi.unit_price) AS revenue
-- FROM order_items oi
-- JOIN products p ON oi.product_id = p.id
-- JOIN categories c ON p.category_id = c.id
-- GROUP BY c.name
-- ORDER BY revenue DESC;
