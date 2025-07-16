-- models/marts/dim_dates.sql
{{ config(materialized='table') }}

WITH date_series AS (
    SELECT generate_series(
        '2023-01-01'::date, -- Adjust start date as needed, e.g., the earliest date in your raw data
        CURRENT_DATE + INTERVAL '1 year', -- Adjust end date as needed (e.g., to cover future data)
        '1 day'::interval
    )::date AS date_day
)
SELECT
    date_day AS date_pk, -- Primary Key for dim_dates
    EXTRACT(YEAR FROM date_day) AS year,
    EXTRACT(MONTH FROM date_day) AS month,
    TO_CHAR(date_day, 'Month') AS month_name,
    EXTRACT(DAY FROM date_day) AS day_of_month,
    EXTRACT(DOW FROM date_day) AS day_of_week, -- 0=Sunday, 1=Monday...
    TO_CHAR(date_day, 'Day') AS day_name,
    EXTRACT(DOY FROM date_day) AS day_of_year,
    EXTRACT(WEEK FROM date_day) AS week_of_year,
    EXTRACT(QUARTER FROM date_day) AS quarter,
    (EXTRACT(YEAR FROM date_day) || '-' || LPAD(EXTRACT(QUARTER FROM date_day)::text, 2, '0')) AS year_quarter,
    (EXTRACT(YEAR FROM date_day) || '-' || LPAD(EXTRACT(MONTH FROM date_day)::text, 2, '0')) AS year_month,
    (EXTRACT(YEAR FROM date_day) || '-' || LPAD(EXTRACT(WEEK FROM date_day)::text, 2, '0')) AS year_week,
    (CASE WHEN EXTRACT(DOW FROM date_day) IN (0, 6) THEN TRUE ELSE FALSE END) AS is_weekend,
    CURRENT_DATE = date_day AS is_current_day
FROM date_series
ORDER BY date_day