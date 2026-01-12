-- Sales trend views for SQLite

-- Hourly breakdown
DROP VIEW IF EXISTS sales_trends_hourly;
CREATE VIEW sales_trends_hourly AS
SELECT
  DATE(o.order_timestamp) AS sales_date,
  CAST(strftime('%H', o.order_timestamp) AS INTEGER) AS sales_hour,
  COUNT(DISTINCT o.order_id) AS orders_count,
  SUM(oi.quantity * oi.item_price) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY DATE(o.order_timestamp), CAST(strftime('%H', o.order_timestamp) AS INTEGER)
ORDER BY sales_date, sales_hour;

-- Weekday vs weekend
DROP VIEW IF EXISTS sales_weekday_vs_weekend;
CREATE VIEW sales_weekday_vs_weekend AS
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
