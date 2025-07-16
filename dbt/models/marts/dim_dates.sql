{{ config(materialized='table') }}

     SELECT
         message_date::DATE AS date,
         EXTRACT(YEAR FROM message_date) AS year,
         EXTRACT(MONTH FROM message_date) AS month,
         EXTRACT(DAY FROM message_date) AS day,
         EXTRACT(DOW FROM message_date) AS day_of_week
     FROM {{ ref('stg_telegram_messages') }}
     GROUP BY message_date::DATE