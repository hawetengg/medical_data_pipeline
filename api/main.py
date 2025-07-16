from fastapi import FastAPI
from pydantic import BaseModel
import psycopg2
from scripts.config import DB_USER, DB_PASSWORD, DB_NAME, DB_HOST, DB_PORT
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="Medical Data API",
    description="API for querying medical product and channel activity data from Telegram.",
    version="1.0.0"
)

# Pydantic models for API responses
class ProductResponse(BaseModel):
    product_name: str
    mention_count: int

class ChannelActivityResponse(BaseModel):
    date: str
    message_count: int

class ImageDetectionResponse(BaseModel):
    message_id: int
    image_path: str
    detected_class: str
    confidence: float
    bbox_xyxy: list[float] # Assuming bbox_xyxy is a list of floats

def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
        )
        logging.info("Database connection established.")
        return conn
    except psycopg2.Error as e:
        logging.error(f"Failed to connect to database: {e}")
        raise

@app.get("/api/reports/top-products", response_model=list[ProductResponse], summary="Get top mentioned products")
async def top_products(limit: int = 10):
    """
    Retrieves the top N products mentioned in Telegram messages based on text content.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT message_text, COUNT(*) as mention_count
            FROM dbt_marts.fct_messages
            WHERE message_text ILIKE '%paracetamol%' OR message_text ILIKE '%antibiotic%' OR message_text ILIKE '%vaccine%' -- Example keywords
            GROUP BY message_text
            ORDER BY mention_count DESC
            LIMIT %s;
        """, (limit,))
        results = cur.fetchall()
        cur.close()
        return [{"product_name": row[0], "mention_count": row[1]} for row in results]
    except psycopg2.Error as e:
        logging.error(f"Error fetching top products: {e}")
        raise # Re-raise for FastAPI to handle as an internal server error
    finally:
        if conn:
            conn.close()

@app.get("/api/channels/{channel_name}/activity", response_model=list[ChannelActivityResponse], summary="Get daily activity for a specific channel")
async def channel_activity(channel_name: str):
    """
    Retrieves the daily message count for a specified Telegram channel.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT dd.date_pk, COUNT(fm.message_id) as message_count
            FROM dbt_marts.fct_messages fm
            JOIN dbt_marts.dim_channels dc ON fm.channel_sk = dc.channel_sk
            JOIN dbt_marts.dim_dates dd ON fm.date_pk = dd.date_pk
            WHERE dc.channel_name = %s
            GROUP BY dd.date_pk
            ORDER BY dd.date_pk;
        """, (channel_name,))
        results = cur.fetchall()
        cur.close()
        return [{"date": str(row[0]), "message_count": row[1]} for row in results]
    except psycopg2.Error as e:
        logging.error(f"Error fetching channel activity: {e}")
        raise
    finally:
        if conn:
            conn.close()

@app.get("/api/images/detections", response_model=list[ImageDetectionResponse], summary="Get all image detections")
async def get_image_detections(limit: int = 100):
    """
    Retrieves a list of image detections with their associated message details.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT
                fid.message_id,
                fid.image_path,
                fid.detected_class,
                fid.confidence,
                fid.bbox_xyxy
            FROM dbt_marts.fct_image_detections fid
            LIMIT %s;
        """, (limit,))
        results = cur.fetchall()
        cur.close()
        # Convert bbox_xyxy from a list of strings (from JSONB) to list of floats if necessary
        # psycopg2 might return JSONB as a Python dict/list directly, so no extra parsing needed if so.
        return [
            {
                "message_id": row[0],
                "image_path": row[1],
                "detected_class": row[2],
                "confidence": row[3],
                "bbox_xyxy": row[4] # This should already be a list/dict from JSONB
            }
            for row in results
        ]
    except psycopg2.Error as e:
        logging.error(f"Error fetching image detections: {e}")
        raise
    finally:
        if conn:
            conn.close()

# You can add more endpoints here as needed for other reports
# e.g., /api/reports/price-trends, /api/reports/visual-content-trends