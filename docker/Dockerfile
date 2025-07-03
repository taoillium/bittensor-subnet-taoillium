FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Set Python path to include current directory
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    procps \
    lsof \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY . .

# Install the current project in development mode
RUN pip install -e .

# Install bittensor-cli separately to handle dependency conflicts
RUN pip install --no-cache-dir bittensor-cli

# Verify bittensor-cli installation
RUN btcli --version

# define build argument
ARG SERVICE_TYPE
ENV SERVICE_TYPE=${SERVICE_TYPE}

# Create entrypoint script
RUN echo '#!/bin/bash\n\
echo "PYTHONPATH: $PYTHONPATH"\n\
echo "Current directory: $(pwd)"\n\
echo "Testing Python import..."\n\
python -c "import sys; print(\"Python path:\", sys.path)"\n\
python -c "import services; print(\"services module imported successfully\")" || echo "Failed to import services"\n\
case "$SERVICE_TYPE" in\n\
    "manager")\n\
        echo "Starting manager service..."\n\
        ./scripts/start_manage.sh\n\
        ;;\n\
    "miner")\n\
        echo "Starting miner service..."\n\
        ./scripts/start_miner.sh\n\
        ;;\n\
    "validator")\n\
        echo "Starting validator service..."\n\
        ./scripts/start_validator.sh\n\
        ;;\n\
    *)\n\
        echo "Unknown service type: $SERVICE_TYPE"\n\
        exit 1\n\
        ;;\n\
esac' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"] 