-- Module 1: Advanced SQL for Analytics Engineering
-- Dataset: bigquery-public-data.thelook_ecommerce.orders

-- Query 1: Basic exploration
SELECT *
FROM `bigquery-public-data.thelook_ecommerce.orders`
LIMIT 10;

-- Query 2: Window function - per-user order sequence numbering
SELECT
  user_id,
  order_id,
  created_at,
  status,
  COUNT(*) OVER (PARTITION BY user_id ORDER BY created_at) AS order_number_for_user
FROM `bigquery-public-data.thelook_ecommerce.orders`
ORDER BY user_id, created_at
LIMIT 20;

-- Query 3: Running total of items ordered per user
SELECT
  user_id,
  order_id,
  created_at,
  status,
  num_of_item,
  SUM(num_of_item) OVER (
    PARTITION BY user_id
    ORDER BY created_at
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_total_items
FROM `bigquery-public-data.thelook_ecommerce.orders`
ORDER BY user_id, created_at
LIMIT 20;

-- Query 4: Deduplication - latest order per user
SELECT
  user_id,
  order_id,
  status,
  created_at,
  ROW_NUMBER() OVER (
    PARTITION BY user_id
    ORDER BY created_at DESC
  ) AS rn
FROM `bigquery-public-data.thelook_ecommerce.orders`
QUALIFY rn = 1
ORDER BY user_id
LIMIT 20;

-- Query 5: Monthly cohort-style aggregation by status
SELECT
  EXTRACT(YEAR FROM created_at) AS order_year,
  EXTRACT(MONTH FROM created_at) AS order_month,
  status,
  COUNT(DISTINCT user_id) AS unique_customers,
  COUNT(*) AS total_orders
FROM `bigquery-public-data.thelook_ecommerce.orders`
GROUP BY order_year, order_month, status
ORDER BY order_year, order_month
LIMIT 20;
