#!/bin/bash

# Management script for Bittensor subnet services
# Usage: ./manage.sh [manager|miner|validator] [start|stop|restart|logs|status] [instance_number]

set -e

SERVICE_TYPE=${1:-manager}
ACTION=${2:-status}
INSTANCE_NUM=${3:-1}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[HEADER]${NC} $1"
}

# Get compose file based on service type
get_compose_file() {
    case $SERVICE_TYPE in
        "manager")
            echo "docker-compose.manager.yml"
            ;;
        "miner")
            echo "docker-compose.miner.yml"
            ;;
        "validator")
            echo "docker-compose.validator.yml"
            ;;
        *)
            print_error "Unknown service type: $SERVICE_TYPE"
            exit 1
            ;;
    esac
}

# Start service
start_service() {
    local compose_file=$(get_compose_file)
    print_status "Starting ${SERVICE_TYPE} service..."
    
    if [ "$SERVICE_TYPE" = "manager" ]; then
        docker-compose -f $compose_file up -d
    else
        # For miner and validator, we need to start specific instance
        docker-compose -f $compose_file up -d ${SERVICE_TYPE}-${INSTANCE_NUM}
    fi
    
    print_status "${SERVICE_TYPE} service started successfully."
}

# Stop service
stop_service() {
    local compose_file=$(get_compose_file)
    print_status "Stopping ${SERVICE_TYPE} service..."
    
    if [ "$SERVICE_TYPE" = "manager" ]; then
        docker-compose -f $compose_file down
    else
        # For miner and validator, we need to stop specific instance
        docker-compose -f $compose_file stop ${SERVICE_TYPE}-${INSTANCE_NUM}
    fi
    
    print_status "${SERVICE_TYPE} service stopped successfully."
}

# Restart service
restart_service() {
    local compose_file=$(get_compose_file)
    print_status "Restarting ${SERVICE_TYPE} service..."
    
    if [ "$SERVICE_TYPE" = "manager" ]; then
        docker-compose -f $compose_file restart
    else
        # For miner and validator, we need to restart specific instance
        docker-compose -f $compose_file restart ${SERVICE_TYPE}-${INSTANCE_NUM}
    fi
    
    print_status "${SERVICE_TYPE} service restarted successfully."
}

# Show logs
show_logs() {
    local compose_file=$(get_compose_file)
    print_status "Showing logs for ${SERVICE_TYPE} service..."
    
    if [ "$SERVICE_TYPE" = "manager" ]; then
        docker-compose -f $compose_file logs -f
    else
        # For miner and validator, we need to show logs for specific instance
        docker-compose -f $compose_file logs -f ${SERVICE_TYPE}-${INSTANCE_NUM}
    fi
}

# Show status
show_status() {
    local compose_file=$(get_compose_file)
    print_header "Status of ${SERVICE_TYPE} service(s):"
    
    if [ "$SERVICE_TYPE" = "manager" ]; then
        docker-compose -f $compose_file ps
    else
        # For miner and validator, show all instances
        docker-compose -f $compose_file ps | grep ${SERVICE_TYPE}
    fi
    
    echo ""
    print_header "Container details:"
    if [ "$SERVICE_TYPE" = "manager" ]; then
        docker-compose -f $compose_file ps -q | xargs docker inspect --format='{{.Name}}: {{.State.Status}} ({{.State.Health.Status}})'
    else
        docker-compose -f $compose_file ps -q | grep ${SERVICE_TYPE} | xargs docker inspect --format='{{.Name}}: {{.State.Status}} ({{.State.Health.Status}})'
    fi
}

# Build service
build_service() {
    local compose_file=$(get_compose_file)
    print_status "Building ${SERVICE_TYPE} service..."
    
    docker-compose -f $compose_file build
    
    print_status "${SERVICE_TYPE} service built successfully."
}

# Pull latest changes
pull_service() {
    local compose_file=$(get_compose_file)
    print_status "Pulling latest changes for ${SERVICE_TYPE} service..."
    
    docker-compose -f $compose_file pull
    
    print_status "Latest changes pulled successfully."
}

# Show help
show_help() {
    echo "Usage: $0 [manager|miner|validator] [start|stop|restart|logs|status|build|pull] [instance_number]"
    echo ""
    echo "Service Types:"
    echo "  manager    - Manager service"
    echo "  miner      - Miner service"
    echo "  validator  - Validator service"
    echo ""
    echo "Actions:"
    echo "  start      - Start the service"
    echo "  stop       - Stop the service"
    echo "  restart    - Restart the service"
    echo "  logs       - Show service logs"
    echo "  status     - Show service status"
    echo "  build      - Build the service"
    echo "  pull       - Pull latest changes"
    echo ""
    echo "Instance Number:"
    echo "  Only required for miner and validator services (default: 1)"
    echo ""
    echo "Examples:"
    echo "  $0 manager start"
    echo "  $0 miner start 2"
    echo "  $0 validator logs 1"
    echo "  $0 manager status"
}

# Main management logic
main() {
    case $ACTION in
        "start")
            start_service
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            restart_service
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "build")
            build_service
            ;;
        "pull")
            pull_service
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "Unknown action: $ACTION"
            show_help
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 