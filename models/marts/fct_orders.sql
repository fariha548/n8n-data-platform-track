select
    o.order_id,
    du.user_key,
    cast(o.created_at as date) as order_date_key,
    o.status,
    o.created_at,
    o.num_of_item,
    sum(oi.sale_price) as order_total_value
from {{ ref('stg_orders') }} o
left join {{ ref('dim_users') }} du
    on o.user_id = du.user_id
    and du.is_current = true
left join {{ ref('stg_order_items') }} oi
    on o.order_id = oi.order_id
group by 1, 2, 3, 4, 5, 6
