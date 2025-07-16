-- models/marts/fct_messages.sql
{{ config(materialized='table') }}

SELECT
    sm.message_id,
    dc.channel_sk, -- Use the correct foreign key from dim_channels
    dd.date_pk,    -- Use the correct foreign key from dim_dates
    sm.message_text,
    sm.has_image,
    sm.photo_path, -- Include photo_path from staging
    sm.source_file, -- Include source_file from staging
    LENGTH(sm.message_text) AS message_length -- Use the correct column name
FROM
    {{ ref('stg_telegram_messages') }} sm -- Alias staging model as 'sm'
LEFT JOIN -- Use LEFT JOIN to keep all messages even if channel/date not found
    {{ ref('dim_channels') }} dc
    ON sm.channel_username = dc.channel_name -- Join on channel_name, not channel_sk directly
LEFT JOIN
    {{ ref('dim_dates') }} dd
    ON sm.message_timestamp::date = dd.date_pk -- Join on the date part of the timestamp