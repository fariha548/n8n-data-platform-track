select
    {{ dbt_utils.generate_surrogate_key(['id']) }} as product_key,
    id as product_id,
    name as product_name,
    category,
    department,
    brand,
    sku,
    cost,
    retail_price,
    distribution_center_id
from {{ source('thelook_ecommerce', 'products') }}
