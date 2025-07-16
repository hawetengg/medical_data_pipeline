import os
import json
import psycopg2
from config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT
from ultralytics import YOLO
import logging
import glob
from datetime import datetime # For parsing date from path if needed

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename='yolo_enrichment.log')

def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        logging.info("Successfully connected to PostgreSQL database.")
        return conn
    except psycopg2.Error as e:
        logging.error(f"Database connection error: {e}")
        raise

def create_raw_detections_table(conn):
    """Creates the raw.yolo_detections table if it doesn't exist."""
    cur = conn.cursor()
    try:
        cur.execute("""
            CREATE SCHEMA IF NOT EXISTS raw;

            CREATE TABLE IF NOT EXISTS raw.yolo_detections (
                detection_id SERIAL PRIMARY KEY,
                message_id BIGINT NOT NULL,
                image_path VARCHAR(512) NOT NULL,
                detected_class VARCHAR(255) NOT NULL,
                confidence REAL NOT NULL,
                bbox_xyxy JSONB,
                detection_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_yolo_detections_message_id ON raw.yolo_detections (message_id);
            CREATE INDEX IF NOT EXISTS idx_yolo_detections_image_path ON raw.yolo_detections (image_path);
        """)
        conn.commit()
        logging.info("raw.yolo_detections table ensured to exist.")
    except psycopg2.Error as e:
        logging.error(f"Error creating raw.yolo_detections table: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()

def get_image_paths(base_image_dir="data/raw/telegram_messages/*/*/images/*.jpg"):
    """
    Collects all image paths based on a glob pattern.
    Assumes image paths like: data/raw/telegram_messages/YYYY-MM-DD/channel_name/images/message_id.jpg
    """
    image_files = glob.glob(base_image_dir, recursive=True)
    logging.info(f"Found {len(image_files)} image files to process from {base_image_dir}")
    return image_files

def extract_message_id_from_path(image_path):
    """
    Extracts the message_id from the image path (e.g., '12345.jpg' -> 12345).
    """
    try:
        filename = os.path.basename(image_path)
        return int(os.path.splitext(filename)[0])
    except (ValueError, IndexError) as e:
        logging.warning(f"Could not extract message_id from image path '{image_path}': {e}")
        return None

def run_yolo_detection_and_store(image_paths_pattern):
    """
    Runs YOLOv8 detection on images and stores results in PostgreSQL.
    """
    conn = None
    try:
        conn = get_db_connection()
        create_raw_detections_table(conn)
        cur = conn.cursor()

        # Load the YOLOv8n model (will download if not present)
        logging.info("Loading YOLOv8n model...")
        model = YOLO('yolov8n.pt') # 'yolov8n.pt' is the nano model, good for quick testing
        logging.info("YOLOv8n model loaded successfully.")

        image_paths = get_image_paths(image_paths_pattern)
        if not image_paths:
            logging.warning("No image files found matching the pattern. Skipping YOLO detection.")
            return

        for image_path in image_paths:
            message_id = extract_message_id_from_path(image_path)
            if message_id is None:
                continue # Skip if message_id cannot be extracted

            try:
                # Run inference on the image
                results = model(image_path)

                # Process results and insert into DB
                for r in results:
                    # r.boxes contains detected bounding boxes and their attributes
                    # r.names is a dictionary mapping class IDs to class names
                    for box in r.boxes:
                        detected_class_id = int(box.cls[0])
                        detected_class_name = model.names[detected_class_id]
                        confidence = float(box.conf[0])
                        bbox_xyxy = box.xyxy[0].tolist() # Convert tensor to list for JSONB

                        cur.execute(
                            """
                            INSERT INTO raw.yolo_detections (
                                message_id, image_path, detected_class, confidence, bbox_xyxy
                            ) VALUES (%s, %s, %s, %s, %s::jsonb);
                            """,
                            (message_id, image_path, detected_class_name, confidence, json.dumps(bbox_xyxy))
                        )
                conn.commit()
                logging.info(f"Processed and stored detections for image: {image_path}")

            except Exception as e:
                logging.error(f"Error processing image {image_path} for YOLO detection: {e}")
                conn.rollback() # Rollback changes for this image if an error occurs

    except Exception as e:
        logging.critical(f"Fatal error during YOLO detection process: {e}")
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    # The glob pattern to find your image files
    # Assumes images are stored like: data/raw/telegram_messages/YYYY-MM-DD/channel_name/images/message_id.jpg
    image_data_path_pattern = "data/raw/telegram_messages/*/*/images/*.jpg"
    
    logging.info(f"Starting YOLO enrichment process for images matching: {image_data_path_pattern}")
    run_yolo_detection_and_store(image_data_path_pattern)
    logging.info("YOLO enrichment process completed.")