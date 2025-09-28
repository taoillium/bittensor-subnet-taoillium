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
    htop \
    netstat-nat \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional monitoring dependencies
RUN pip install --no-cache-dir psutil

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
\n\
# Set resource limits\n\
ulimit -n 65536\n\
ulimit -u 32768\n\
\n\
# Start service with resource monitoring\n\
echo "Starting service with resource monitoring..."\n\
./scripts/start_with_monitor.sh' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"] 