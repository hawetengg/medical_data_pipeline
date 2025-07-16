{{ config(materialized='table') }}

SELECT
    {{ dbt_utils.generate_surrogate_key(['channel_username']) }} AS channel_sk, -- Stable surrogate key
    channel_username AS channel_name,
    'Telegram' AS platform_source
FROM
    {{ ref('stg_telegram_messages') }}
WHERE
    channel_username IS NOT NULL