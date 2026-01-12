-- KPI views for SQLite

-- Daily revenue and orders
DROP VIEW IF EXISTS kpi_daily_revenue;
CREATE VIEW kpi_daily_revenue AS
SELECT
  DATE(o.order_timestamp) AS sales_date,
  COUNT(DISTINCT o.order_id) AS orders_count,
  SUM(oi.quantity * oi.item_price) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY DATE(o.order_timestamp);

-- Average order value
DROP VIEW IF EXISTS kpi_average_order_value;
CREATE VIEW kpi_average_order_value AS
SELECT
  DATE(o.order_timestamp) AS sales_date,
  SUM(oi.quantity * oi.item_price) * 1.0 / COUNT(DISTINCT o.order_id) AS average_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY DATE(o.order_timestamp);

-- Revenue by category
DROP VIEW IF EXISTS kpi_revenue_by_category;
CREATE VIEW kpi_revenue_by_category AS
SELECT
  c.category_name,
  SUM(oi.quantity * oi.item_price) AS total_revenue
FROM order_items oi
JOIN menu_items mi ON oi.menu_item_id = mi.menu_item_id
JOIN categories c ON mi.category_id = c.category_id
GROUP BY c.category_name;

-- Revenue per hour
DROP VIEW IF EXISTS kpi_revenue_per_hour;
CREATE VIEW kpi_revenue_per_hour AS
SELECT
  CAST(strftime('%H', o.order_timestamp) AS INTEGER) AS sales_hour,
  COUNT(DISTINCT o.order_id) AS orders_count,
  SUM(oi.quantity * oi.item_price) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY CAST(strftime('%H', o.order_timestamp) AS INTEGER);

-- Top menu items
DROP VIEW IF EXISTS kpi_top_menu_items;
CREATE VIEW kpi_top_menu_items AS
SELECT
  mi.item_name,
  SUM(oi.quantity) AS total_quantity,
  SUM(oi.quantity * oi.item_price) AS total_revenue
FROM order_items oi
JOIN menu_items mi ON oi.menu_item_id = mi.menu_item_id
GROUP BY mi.item_name
ORDER BY total_revenue DESC;

-- Weekday vs weekend
DROP VIEW IF EXISTS kpi_weekday_vs_weekend;
CREATE VIEW kpi_weekday_vs_weekend AS
SELECT
  CASE
    WHEN CAST(strftime('%w', o.order_timestamp) AS INTEGER) IN (0, 6) THEN 'weekend'
    ELSE 'weekday'
  END AS day_type,
  COUNT(DISTINCT o.order_id) AS orders_count,
  SUM(oi.quantity * oi.item_price) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY CASE
  WHEN CAST(strftime('%w', o.order_timestamp) AS INTEGER) IN (0, 6) THEN 'weekend'
  ELSE 'weekday'
END;
