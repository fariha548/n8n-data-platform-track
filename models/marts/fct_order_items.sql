select
    oi.order_item_id,
    oi.order_id,
    du.user_key,
    dp.product_key,
    cast(o.created_at as date) as order_date_key,
    oi.sale_price
from {{ ref('stg_order_items') }} oi
left join {{ ref('stg_orders') }} o
    on oi.order_id = o.order_id
left join {{ ref('dim_users') }} du
    on o.user_id = du.user_id
    and du.is_current = true
left join {{ ref('dim_products') }} dp
    on oi.product_id = dp.product_id
