-- Time-series sales trends with hourly breakdown
CREATE OR REPLACE VIEW sales_trends_hourly AS
SELECT
  DATE(o.order_timestamp) AS sales_date,
  EXTRACT(HOUR FROM o.order_timestamp) AS sales_hour,
  COUNT(DISTINCT o.order_id) AS orders_count,
  SUM(oi.quantity * oi.item_price) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY DATE(o.order_timestamp), EXTRACT(HOUR FROM o.order_timestamp)
ORDER BY sales_date, sales_hour;

-- Weekday vs weekend performance
CREATE OR REPLACE VIEW sales_weekday_vs_weekend AS
SELECT
  CASE
    WHEN EXTRACT(DOW FROM o.order_timestamp) IN (0, 6) THEN 'weekend'
    ELSE 'weekday'
  END AS day_type,
  COUNT(DISTINCT o.order_id) AS orders_count,
  SUM(oi.quantity * oi.item_price) AS total_revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY CASE
  WHEN EXTRACT(DOW FROM o.order_timestamp) IN (0, 6) THEN 'weekend'
  ELSE 'weekday'
END;

