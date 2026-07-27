SELECT
  id AS order_item_id,
  order_id,
  user_id,
  product_id,
  sale_price,
  status,
  created_at
FROM {{ source('thelook_ecommerce', 'order_items') }}
-- concurrent retest B
