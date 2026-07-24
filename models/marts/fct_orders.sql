SELECT
  o.order_id,
  o.user_id,
  u.first_name,
  u.last_name,
  u.country,
  o.status,
  o.created_at,
  o.num_of_item,
  SUM(oi.sale_price) AS order_total_value
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('stg_users') }} u ON o.user_id = u.user_id
LEFT JOIN {{ ref('stg_order_items') }} oi ON o.order_id = oi.order_id
GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
