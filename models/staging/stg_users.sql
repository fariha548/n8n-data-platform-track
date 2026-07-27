SELECT
  id AS user_id,
  first_name,
  last_name,
  email,
  age,
  gender,
  city,
  state,
  country,
  created_at
FROM {{ source('thelook_ecommerce', 'users') }}
-- concurrent retest A
