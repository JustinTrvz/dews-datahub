# Base image that includes Python and GDAL
FROM ghcr.io/osgeo/gdal:ubuntu-small-3.8.0

# Install OS packages
RUN apt update && apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-gdal \
    python3-brlapi \
    libpq-dev \
    rsync \
    wget \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
RUN mkdir -p /app

# Copy Python Django application
COPY dews /app/dews
COPY ./entrypoint.sh /app

# Add application's project path to Python path
ENV PYTHONPATH="${PYTHONPATH}:/app:/app/dews"

# Install Python packages
WORKDIR /app/dews
RUN pip install --no-cache-dir -r requirements.txt

# Execute "entrypoint.sh"
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
