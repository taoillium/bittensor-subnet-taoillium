#!/bin/bash

# Emergency cleanup script for resource exhaustion
# This script should be run when the system is experiencing resource issues

echo "=== Emergency Resource Cleanup Script ==="
echo "Timestamp: $(date)"
echo ""

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    log "WARNING: Not running as root. Some operations may fail."
fi

log "Starting emergency cleanup..."

# 1. Kill zombie processes
log "Cleaning up zombie processes..."
ps aux | awk '$8 ~ /^Z/ { print $2 }' | xargs -r kill -9 2>/dev/null

# 2. Clean up Docker resources
log "Cleaning up Docker resources..."
if command -v docker &> /dev/null; then
    # Stop all containers
    docker stop $(docker ps -q) 2>/dev/null || true
    
    # Remove stopped containers
    docker container prune -f 2>/dev/null || true
    
    # Remove unused networks
    docker network prune -f 2>/dev/null || true
    
    # Remove unused volumes
    docker volume prune -f 2>/dev/null || true
    
    # Remove unused images
    docker image prune -f 2>/dev/null || true
    
    # System prune
    docker system prune -f 2>/dev/null || true
fi

# 3. Clean up system temporary files
log "Cleaning up temporary files..."
find /tmp -type f -mtime +1 -delete 2>/dev/null || true
find /var/tmp -type f -mtime +1 -delete 2>/dev/null || true

# 4. Clean up old log files
log "Cleaning up old log files..."
find /var/log -name "*.log.*" -mtime +7 -delete 2>/dev/null || true
find /app/logs -name "*.log.*" -mtime +3 -delete 2>/dev/null || true

# 5. Clear system caches
log "Clearing system caches..."
sync
echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true

# 6. Kill processes consuming too much memory
log "Checking for memory-intensive processes..."
ps aux --sort=-%mem | head -10 | while read line; do
    pid=$(echo $line | awk '{print $2}')
    mem_percent=$(echo $line | awk '{print $4}')
    if (( $(echo "$mem_percent > 50" | bc -l) )); then
        process_name=$(echo $line | awk '{print $11}')
        log "High memory process found: PID $pid ($process_name) using ${mem_percent}% memory"
    fi
done

# 7. Check file descriptor usage
log "Checking file descriptor usage..."
if [ -f /proc/sys/fs/file-nr ]; then
    fd_info=$(cat /proc/sys/fs/file-nr)
    used_fds=$(echo $fd_info | awk '{print $1}')
    max_fds=$(echo $fd_info | awk '{print $3}')
    fd_percent=$((used_fds * 100 / max_fds))
    log "File descriptors: $used_fds/$max_fds (${fd_percent}%)"
    
    if [ $fd_percent -gt 80 ]; then
        log "WARNING: High file descriptor usage detected!"
    fi
fi

# 8. Check network connections
log "Checking network connections..."
connection_count=$(ss -tuln | wc -l)
log "Active network connections: $connection_count"

# 9. Restart Docker daemon if needed
if command -v docker &> /dev/null; then
    docker_info=$(docker info 2>&1)
    if echo "$docker_info" | grep -q "Cannot connect"; then
        log "Docker daemon appears to be unresponsive, attempting restart..."
        systemctl restart docker 2>/dev/null || service docker restart 2>/dev/null || true
        sleep 5
    fi
fi

# 10. Final system status
log "Final system status:"
echo "Memory usage:"
free -h
echo ""
echo "Disk usage:"
df -h
echo ""
echo "Top processes by memory:"
ps aux --sort=-%mem | head -5
echo ""
echo "Top processes by CPU:"
ps aux --sort=-%cpu | head -5

log "Emergency cleanup completed!"
echo "=== End of Emergency Cleanup ==="
