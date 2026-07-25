{{ config(materialized='table') }}

with date_spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2019-01-01' as date)",
        end_date="cast('2026-12-31' as date)"
    ) }}
)

select
    cast(date_day as date) as date_key,
    extract(year from date_day) as year,
    extract(quarter from date_day) as quarter,
    extract(month from date_day) as month,
    format_date('%B', date_day) as month_name,
    extract(day from date_day) as day_of_month,
    extract(dayofweek from date_day) as day_of_week,
    format_date('%A', date_day) as day_name,
    extract(week from date_day) as week_of_year
from date_spine
