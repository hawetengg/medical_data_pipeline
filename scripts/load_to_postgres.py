import json
     import psycopg2
     from config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT
     import glob
     import logging

     logging.basicConfig(filename='load.log', level=logging.INFO)

     def load_json_to_postgres(json_dir, table_name="raw.telegram_messages"):
         conn = psycopg2.connect(
             dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
         )
         cur = conn.cursor()
         cur.execute(f"""
             CREATE SCHEMA IF NOT EXISTS raw;
             CREATE TABLE IF NOT EXISTS {table_name} (
                 id BIGINT,
                 channel VARCHAR,
                 date TIMESTAMP,
                 text TEXT,
                 has_image BOOLEAN,
                 photo_path VARCHAR
             )
         """)
         for json_file in glob.glob(f"{json_dir}/*.json"):
             with open(json_file, 'r') as f:
                 data = json.load(f)
                 for msg in data:
                     cur.execute(
                         f"INSERT INTO {table_name} (id, channel, date, text, has_image, photo_path) VALUES (%s, %s, %s, %s, %s, %s)",
                         (msg["id"], json_file.split("/")[-2], msg["date"], msg["text"], msg["has_image"], msg.get("photo_path"))
                     )
             logging.info(f"Loaded {json_file} to {table_name}")
         conn.commit()
         cur.close()
         conn.close()

     if __name__ == "__main__":
         load_json_to_postgres("data/raw/telegram_messages/*/*")