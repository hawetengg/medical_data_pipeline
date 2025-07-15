# Medical Data Pipeline
10 Academy Week 7 Challenge: An end-to-end data pipeline for analyzing Ethiopian medical businesses using Telegram data.

## Project Structure
- `data/`: Raw, staging, and mart data.
- `dbt/`: dbt models and tests.
- `scripts/`: Data scraping, loading, and enrichment scripts.
- `api/`: FastAPI application for analytical endpoints.
- `Dockerfile`, `docker-compose.yml`: Containerized environment.
- `requirements.txt`: Python dependencies.

## Setup
1. Clone the repo: `git clone https://github.com/your-username/medical_data_pipeline.git`
2. Set up environment variables in `.env`.
3. Run: `docker-compose up --build`