-- models/marts/fct_image_detections.sql
{{ config(materialized='table') }}

SELECT
    syd.detection_id,
    syd.message_id,
    syd.image_path,
    syd.detected_class,
    syd.confidence,
    syd.bbox_xyxy,
    syd.detection_timestamp,
    fmsg.channel_sk, -- Join with fct_messages to get channel_sk
    fmsg.date_pk     -- Join with fct_messages to get date_pk
FROM
    {{ ref('stg_yolo_detections') }} syd
LEFT JOIN
    {{ ref('fct_messages') }} fmsg
    ON syd.message_id = fmsg.message_id
WHERE
    syd.detected_class IS NOT NULL -- Only include detections with a class