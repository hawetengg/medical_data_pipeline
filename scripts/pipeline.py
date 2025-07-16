import os
import subprocess
from datetime import datetime
import logging # Import logging
from dagster import job, op, schedule, Definitions

# Configure logging for Dagster
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Corrected imports for your scripts
from scripts.scrape_telegram import scrape_channel
from scripts.load_to_postgres import load_json_to_postgres
from scripts.yolo_enrichment import run_yolo_detection_and_store # Corrected function name

# Define constants for paths
# These paths are relative to the /app WORKDIR in the Docker container
RAW_DATA_BASE_DIR = "data/raw/telegram_messages"
DBT_PROJECT_DIR = "medical_data_dbt"
IMAGE_DATA_PATTERN = "data/raw/telegram_messages/*/*/images/*.jpg"

@op
def scrape_op():
    """
    Scrapes Telegram messages for specified channels and saves raw data to files.
    """
    channels = ["Chemed", "lobelia4cosmetics", "tikvahpharma"]
    today_str = datetime.now().strftime('%Y-%m-%d')
    
    logging.info(f"Starting Telegram scraping for date: {today_str}")
    for channel in channels:
        output_dir = os.path.join(RAW_DATA_BASE_DIR, today_str, channel)
        logging.info(f"Scraping channel {channel} to {output_dir}")
        scrape_channel(f"https://t.me/{channel}", output_dir)
    logging.info("Telegram scraping completed.")

@op
def load_to_postgres_op():
    """
    Loads scraped JSON data from files into the raw.telegram_messages PostgreSQL table.
    """
    # The load_json_to_postgres function expects a glob pattern
    input_pattern = os.path.join(RAW_DATA_BASE_DIR, "*", "*")
    logging.info(f"Loading JSON data to PostgreSQL from pattern: {input_pattern}")
    load_json_to_postgres(input_pattern)
    logging.info("JSON data loading to PostgreSQL completed.")

@op
def dbt_run_op():
    """
    Executes dbt run to transform data in the data warehouse.
    """
    logging.info(f"Running dbt transformations in project: {DBT_PROJECT_DIR}")
    # The subprocess command needs to be run from the /app directory
    # and reference the dbt project correctly.
    # Using cwd ensures the command is run from the correct directory.
    result = subprocess.run(
        ["dbt", "run"],
        cwd=DBT_PROJECT_DIR, # Run dbt from within the medical_data_dbt directory
        capture_output=True,
        text=True,
        check=False # Do not raise an exception for non-zero exit codes immediately
    )
    logging.info(f"dbt run stdout:\n{result.stdout}")
    if result.stderr:
        logging.error(f"dbt run stderr:\n{result.stderr}")
    result.check_returncode() # Raise CalledProcessError if dbt run failed
    logging.info("dbt transformations completed successfully.")

@op
def yolo_enrichment_op():
    """
    Runs YOLO object detection on images and stores results in PostgreSQL.
    """
    logging.info(f"Starting YOLO enrichment for images matching: {IMAGE_DATA_PATTERN}")
    run_yolo_detection_and_store(IMAGE_DATA_PATTERN)
    logging.info("YOLO enrichment completed.")

@job
def medical_data_pipeline():
    """
    The main data pipeline job, orchestrating scraping, loading, dbt, and YOLO enrichment.
    """
    # Define dependencies using the >> operator
    scrape_op_result = scrape_op()
    load_op_result = load_to_postgres_op(start_after=scrape_op_result) # Explicit dependency
    dbt_run_op_result = dbt_run_op(start_after=load_op_result) # Explicit dependency
    yolo_enrichment_op(start_after=dbt_run_op_result) # Explicit dependency


@schedule(cron_schedule="0 0 * * *", job=medical_data_pipeline, name="daily_medical_data_pipeline")
def daily_pipeline_schedule(context):
    """
    Schedules the medical_data_pipeline to run daily at midnight.
    """
    # You can add run configuration here if needed
    return {}

# Define your Dagster repository
# This tells Dagster what jobs, schedules, etc., are available in this file.
defs = Definitions(
    jobs=[medical_data_pipeline],
    schedules=[daily_pipeline_schedule],
)