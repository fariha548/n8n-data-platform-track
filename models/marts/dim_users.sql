select
    {{ dbt_utils.generate_surrogate_key(['id', 'dbt_valid_from']) }} as user_key,
    id as user_id,
    first_name,
    last_name,
    email,
    age,
    gender,
    state,
    nullif(city, 'null') as city,
    country,
    traffic_source,
    dbt_valid_from,
    dbt_valid_to,
    (dbt_valid_to is null) as is_current
from {{ ref('users_snapshot') }}
