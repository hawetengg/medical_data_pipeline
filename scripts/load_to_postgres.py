import json
import psycopg2
from config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT
import glob
import logging
import os
from datetime import datetime

logging.basicConfig(filename='load.log', level=logging.INFO)

def load_json_to_postgres(json_dir, table_name="raw.telegram_messages"):
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()

        cur.execute(f"CREATE SCHEMA IF NOT EXISTS raw;")

        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id BIGINT,
                channel VARCHAR,
                date TIMESTAMP,
                text TEXT,
                has_image BOOLEAN,
                photo_path VARCHAR,
                source_file VARCHAR
            );
        """)
        conn.commit()

        json_files = glob.glob(json_dir, recursive=True)
        logging.info(f"Found {len(json_files)} JSON files to load from {json_dir}")

        for json_file_path in json_files:
            try:
                with open(json_file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                path_parts = json_file_path.split(os.sep)
                if len(path_parts) >= 2:
                    channel_name = path_parts[-2]
                else:
                    channel_name = "unknown_channel"

                for msg in data:
                    msg_id = msg.get("id")
                    msg_date = msg.get("date")
                    msg_text = msg.get("text")
                    msg_has_image = msg.get("has_image")
                    msg_photo_path = msg.get("photo_path")

                    cur.execute(
                        f"INSERT INTO {table_name} (id, channel, date, text, has_image, photo_path, source_file) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (msg_id, channel_name, msg_date, msg_text, msg_has_image, msg_photo_path, json_file_path)
                    )
                conn.commit()
                logging.info(f"Successfully loaded data from {json_file_path} to {table_name}")

            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {json_file_path}: {e}")
                if conn: conn.rollback()
            except Exception as e:
                logging.error(f"Error processing file {json_file_path}: {e}")
                if conn: conn.rollback()

    except psycopg2.Error as e:
        logging.error(f"Database connection or operation error: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        logging.info("Database connection closed.")


if __name__ == "__main__":
    json_data_path = "data/raw/telegram_messages/*/*/*.json"
    
    logging.info(f"Starting data load from {json_data_path} to PostgreSQL...")
    load_json_to_postgres(json_data_path)
    logging.info("Data load process completed.")