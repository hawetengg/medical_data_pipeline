FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

ENV PIP_DEFAULT_TIMEOUT=3000 

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
# Note: pip handles dependencies, so as long as they are all available locally,
# the order below is generally safe, but installing common ones first is good.
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
# MAKE SURE 'ultralytics' IS UNCOMMENTED IN requirements.txt if it was commented out.
# torch and torchvision should NOT be listed directly in requirements.txt if manually installed here.
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["tail", "-f", "/dev/null"]