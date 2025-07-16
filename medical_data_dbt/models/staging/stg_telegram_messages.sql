-- models/staging/stg_telegram_messages.sql
{{ config(materialized='view') }}

SELECT
    id AS message_id,
    channel AS channel_username, -- <-- CORRECTED: Alias 'channel' to 'channel_username'
    date::TIMESTAMP AS message_timestamp, -- Changed to message_timestamp for consistency with dim_channels
    text AS message_text, -- Changed to message_text for consistency
    has_image,
    photo_path,
    source_file -- Ensure this column is selected if it exists in raw.telegram_messages
FROM
    {{ source('raw', 'telegram_messages') }}
WHERE
    text IS NOT NULL