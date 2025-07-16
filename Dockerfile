FROM python:3.10-slim

WORKDIR /app

# Install system dependencies required by opencv-python (used by ultralytics)
# and psycopg2 (for database connection)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libgirepository1.0-dev \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    build-essential \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Set PIP timeout before copying requirements and wheels
ENV PIP_DEFAULT_TIMEOUT=3000

# Copy requirements.txt for initial installs
COPY requirements.txt .

# Install typing-extensions from default PyPI (it's small and generally reliable)
RUN pip install typing-extensions>=4.10.0

# --- START MANUAL INSTALLATIONS ---
# Copy all downloaded wheel files into the container
COPY filelock-3.13.1-py3-none-any.whl .
COPY fsspec-2024.6.1-py3-none-any.whl .
COPY Jinja2-3.1.3-py3-none-any.whl .
COPY MarkupSafe-2.1.5-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl .
COPY mpmath-1.3.0-py3-none-any.whl .
COPY networkx-3.3-py3-none-any.whl .
COPY numpy-2.1.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl .
COPY pillow-11.0.0-cp310-cp310-manylinux_2_28_x86_64.whl .
COPY sympy-1.13.3-py3-none-any.whl .
COPY torch-2.7.1+cpu-cp310-cp310-manylinux_2_28_x86_64.whl .
COPY torchvision-0.22.1+cpu-cp310-cp310-manylinux_2_28_x86_64.whl .

# Install dependencies in an order that respects requirements
RUN pip install --no-cache-dir \
    ./filelock-3.13.1-py3-none-any.whl \
    ./fsspec-2024.6.1-py3-none-any.whl \
    ./Jinja2-3.1.3-py3-none-any.whl \
    ./MarkupSafe-2.1.5-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl \
    ./mpmath-1.3.0-py3-none-any.whl \
    ./networkx-3.3-py3-none-any.whl \
    ./numpy-2.1.2-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl \
    ./pillow-11.0.0-cp310-cp310-manylinux_2_28_x86_64.whl \
    ./sympy-1.13.3-py3-none-any.whl \
    ./torch-2.7.1+cpu-cp310-cp310-manylinux_2_28_x86_64.whl \
    ./torchvision-0.22.1+cpu-cp310-cp310-manylinux_2_28_x86_64.whl

# --- END MANUAL INSTALLATIONS ---

# Then install the rest of requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose port 8000 for FastAPI (if you add FastAPI later)
EXPOSE 8000

CMD ["tail", "-f", "/dev/null"]