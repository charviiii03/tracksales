-- Insert sample customers
INSERT INTO customers (name, email, phone, address) VALUES
('John Smith', 'john.smith@email.com', '555-0101', '123 Main St, City'),
('Sarah Johnson', 'sarah.j@email.com', '555-0102', '456 Oak Ave, Town'),
('Michael Brown', 'michael.b@email.com', '555-0103', '789 Pine Rd, Village'),
('Emma Davis', 'emma.d@email.com', '555-0104', '321 Elm St, Borough'),
('James Wilson', 'james.w@email.com', '555-0105', '654 Maple Dr, District');

-- Insert sample products
INSERT INTO products (name, description, price, stock) VALUES
('Laptop Pro X', 'High-performance laptop with SSD', 1299.99, 15),
('Smartphone Y', 'Latest model with 5G capability', 799.99, 25),
('Tablet Z', '10-inch display tablet', 499.99, 8),
('Wireless Earbuds', 'Noise-canceling bluetooth earbuds', 149.99, 5),
('Smart Watch', 'Fitness tracking smartwatch', 249.99, 12),
('Power Bank', '20000mAh portable charger', 49.99, 30),
('USB-C Cable', 'Fast charging cable 2m length', 19.99, 50),
('Laptop Bag', 'Professional laptop carrying case', 59.99, 18);

-- Insert sample sales and sales items (assuming admin user_id is 1)
INSERT INTO sales (customer_id, user_id, total_amount, sale_date) VALUES
(1, 1, 2099.97, DATE_SUB(NOW(), INTERVAL 1 DAY)),
(2, 1, 849.98, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(3, 1, 1499.98, CURDATE()),
(4, 1, 299.98, CURDATE()),
(5, 1, 569.97, CURDATE());

-- Insert sample sales items
INSERT INTO sales_items (sale_id, product_id, quantity, price) VALUES
(1, 1, 1, 1299.99),
(1, 4, 2, 149.99),
(2, 2, 1, 799.99),
(2, 7, 2, 19.99),
(3, 1, 1, 1299.99),
(3, 8, 1, 59.99),
(4, 4, 2, 149.99),
(5, 5, 2, 249.99),
(5, 6, 1, 49.99);