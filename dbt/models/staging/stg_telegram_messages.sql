{{ config(materialized='view') }}

     SELECT
         id,
         channel,
         date::TIMESTAMP AS message_date,
         text,
         has_image,
         photo_path
     FROM raw.telegram_messages
     WHERE text IS NOT NULL