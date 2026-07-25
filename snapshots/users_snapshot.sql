{% snapshot users_snapshot %}
{{
    config(
      target_schema='snapshots',
      unique_key='id',
      strategy='check',
      check_cols=['state', 'city', 'postal_code', 'street_address', 'traffic_source'],
      invalidate_hard_deletes=True
    )
}}
select * from {{ source('thelook_ecommerce', 'users') }}
{% endsnapshot %}
