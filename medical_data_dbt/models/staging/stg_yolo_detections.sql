-- models/staging/stg_yolo_detections.sql
{{ config(materialized='view') }}

SELECT
    detection_id,
    message_id,
    image_path,
    detected_class,
    confidence,
    bbox_xyxy,
    detection_timestamp
FROM
    {{ source('raw', 'yolo_detections') }}