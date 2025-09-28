#!/bin/bash

# Start service with resource monitoring
# This script starts the main service and resource monitor in parallel

CURRENT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "${CURRENT_DIR}/env.sh"

cd $CURRENT_DIR/../

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to cleanup background processes
cleanup() {
    echo "Shutting down services..."
    if [ ! -z "$MAIN_PID" ]; then
        kill $MAIN_PID 2>/dev/null
    fi
    if [ ! -z "$MONITOR_PID" ]; then
        kill $MONITOR_PID 2>/dev/null
    fi
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start resource monitor in background
echo "Starting resource monitor..."
python scripts/resource_monitor.py &
MONITOR_PID=$!

# Wait a moment for monitor to start
sleep 2

# Start main service based on SERVICE_TYPE
case "$SERVICE_TYPE" in
    "manager")
        echo "Starting manager service..."
        python -m manage.main &
        MAIN_PID=$!
        ;;
    "miner")
        echo "Starting miner service..."
        ./scripts/start_miner.sh &
        MAIN_PID=$!
        ;;
    "validator")
        echo "Starting validator service..."
        ./scripts/start_validator.sh &
        MAIN_PID=$!
        ;;
    *)
        echo "Unknown service type: $SERVICE_TYPE"
        cleanup
        exit 1
        ;;
esac

# Wait for main process
wait $MAIN_PID
MAIN_EXIT_CODE=$?

# Cleanup monitor
kill $MONITOR_PID 2>/dev/null
wait $MONITOR_PID 2>/dev/null

echo "Service exited with code: $MAIN_EXIT_CODE"
exit $MAIN_EXIT_CODE
