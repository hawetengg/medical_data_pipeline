from ultralytics import YOLO
     import psycopg2
     from config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT
     import glob
     import logging

     logging.basicConfig(filename='yolo.log', level=logging.INFO)

     def run_yolo(image_dir):
         model = YOLO("yolov8n.pt")
         conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
         cur = conn.cursor()
         cur.execute("""
             CREATE SCHEMA IF NOT EXISTS marts;
             CREATE TABLE IF NOT EXISTS marts.fct_image_detections (
                 message_id BIGINT,
                 detected_object_class VARCHAR,
                 confidence_score FLOAT
             )
         """)
         for image_path in glob.glob(f"{image_dir}/*.jpg"):
             message_id = int(image_path.split("/")[-1].split(".")[0])
             results = model(image_path)
             for result in results:
                 for box in result.boxes:
                     cur.execute(
                         "INSERT INTO marts.fct_image_detections (message_id, detected_object_class, confidence_score) VALUES (%s, %s, %s)",
                         (message_id, result.names[int(box.cls)], box.conf.item())
                     )
             logging.info(f"Processed {image_path}")
         conn.commit()
         cur.close()
         conn.close()

     if __name__ == "__main__":
         run_yolo("data/raw/telegram_messages/*/*/images")