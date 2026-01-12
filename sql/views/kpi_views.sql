-- Daily revenue and orders
CREATE OR REPLACE VIEW kpi_daily_revenue AS
SELECT
  DATE(o.order_timestamp) AS sales_date,
  COUNT(DISTINCT o.order_id) AS orders_count,
  SUM(oi.quantity * oi.item_price) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY DATE(o.order_timestamp);

-- Average order value (AOV)
CREATE OR REPLACE VIEW kpi_average_order_value AS
SELECT
  DATE(o.order_timestamp) AS sales_date,
  SUM(oi.quantity * oi.item_price) / NULLIF(COUNT(DISTINCT o.order_id), 0) AS average_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY DATE(o.order_timestamp);

-- Revenue by category
CREATE OR REPLACE VIEW kpi_revenue_by_category AS
SELECT
  c.category_name,
  SUM(oi.quantity * oi.item_price) AS total_revenue
FROM order_items oi
JOIN menu_items mi ON oi.menu_item_id = mi.menu_item_id
JOIN categories c ON mi.category_id = c.category_id
GROUP BY c.category_name;

