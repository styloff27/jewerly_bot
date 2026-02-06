INSERT OR REPLACE INTO customers (id, name, email, phone) VALUES
(1, "Alice Chen", "alice@example.com", "+1-555-0101"),
(2, "Bob Martinez", "bob@example.com", "+1-555-0102"),
(3, "Carol Webb", "carol@example.com", "+1-555-0103"),
(4, "David Lee", "david@example.com", "+1-555-0104"),
(5, "Eve Johnson", "eve@example.com", "+1-555-0105"),
(6, "Frank Brown", "frank@example.com", "+1-555-0106");


 INSERT OR REPLACE INTO orders (id, customer_id, status, price) VALUES
    (1, 1, "shipped", 24900),
    (2, 1, "pending", 8900.00),
    (3, 2, "delivered", 15600.00),
    (4, 3, "pending", 42000.00);

INSERT OR REPLACE INTO inventory (id, sku, name, quantity, unit) VALUES
    (1, "RING-001", "Silver band ring", 12, "piece"),
    (2, "NECK-002", "Gold pendant necklace", 5, "piece"),
    (3, "BRAC-003", "Pearl bracelet", 0, "piece"),
    (4, "EAR-004", "Stud earrings set", 24, "piece");

INSERT OR REPLACE INTO notes (id, customer_id, order_id, content) VALUES
    (1, 1, 2, "Pred contact: email. Interested in custom engraving."),
    (2, 2, 3, "Order 3: customer requested gift wrap."),
    (3, 1, 4, "Large order – confirm stock before shipping."),
    (4, 3, 3, "Follow up next week re: wedding collection.");