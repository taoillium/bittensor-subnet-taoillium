#!/usr/bin/env python3
"""
Resource Monitor and Cleanup Script
Monitors system resources and performs cleanup to prevent resource exhaustion
"""

import os
import sys
import time
import psutil
import logging
import signal
import gc
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/resource_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ResourceMonitor:
    """Monitor and manage system resources"""
    
    def __init__(self):
        self.running = True
        self.cleanup_thresholds = {
            'memory_percent': 85.0,  # Memory usage threshold (optimized for 8GB)
            'cpu_percent': 95.0,     # CPU usage threshold (allow higher usage)
            'file_descriptors': 60000,  # File descriptor threshold (increased)
            'connections': 15000,    # Network connection threshold (increased)
        }
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = 0
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def get_system_stats(self) -> Dict:
        """Get current system resource statistics"""
        try:
            # Memory stats
            memory = psutil.virtual_memory()
            
            # CPU stats
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # File descriptor count
            fd_count = 0
            try:
                with open('/proc/sys/fs/file-nr', 'r') as f:
                    fd_count = int(f.read().split()[0])
            except (FileNotFoundError, PermissionError):
                # Fallback for systems without /proc
                fd_count = len(psutil.Process().open_files())
            
            # Network connections
            connections = len(psutil.net_connections())
            
            # Process count
            process_count = len(psutil.pids())
            
            return {
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'memory_used_gb': memory.used / (1024**3),
                'cpu_percent': cpu_percent,
                'file_descriptors': fd_count,
                'connections': connections,
                'process_count': process_count,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            return {}
    
    def check_resource_thresholds(self, stats: Dict) -> List[str]:
        """Check if any resource thresholds are exceeded"""
        warnings = []
        
        if stats.get('memory_percent', 0) > self.cleanup_thresholds['memory_percent']:
            warnings.append(f"High memory usage: {stats['memory_percent']:.1f}%")
        
        if stats.get('cpu_percent', 0) > self.cleanup_thresholds['cpu_percent']:
            warnings.append(f"High CPU usage: {stats['cpu_percent']:.1f}%")
        
        if stats.get('file_descriptors', 0) > self.cleanup_thresholds['file_descriptors']:
            warnings.append(f"High file descriptor count: {stats['file_descriptors']}")
        
        if stats.get('connections', 0) > self.cleanup_thresholds['connections']:
            warnings.append(f"High connection count: {stats['connections']}")
        
        return warnings
    
    def perform_cleanup(self):
        """Perform system cleanup operations"""
        logger.info("Performing system cleanup...")
        
        try:
            # Force garbage collection
            collected = gc.collect()
            logger.info(f"Garbage collected {collected} objects")
            
            # Clean up Python cache
            self._cleanup_python_cache()
            
            # Clean up temporary files
            self._cleanup_temp_files()
            
            # Clean up old log files
            self._cleanup_old_logs()
            
            # Force sync to disk
            os.sync()
            
            logger.info("Cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def _cleanup_python_cache(self):
        """Clean up Python cache files"""
        try:
            import shutil
            cache_dirs = [
                '/app/__pycache__',
                '/app/services/__pycache__',
                '/app/neurons/__pycache__',
                '/app/template/__pycache__',
                '/app/manage/__pycache__'
            ]
            
            for cache_dir in cache_dirs:
                if os.path.exists(cache_dir):
                    shutil.rmtree(cache_dir)
                    logger.debug(f"Removed cache directory: {cache_dir}")
        except Exception as e:
            logger.error(f"Error cleaning Python cache: {e}")
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import tempfile
            import glob
            
            # Clean up /tmp files older than 1 hour
            temp_patterns = [
                '/tmp/tmp*',
                '/tmp/python*',
                '/app/logs/*.tmp'
            ]
            
            for pattern in temp_patterns:
                for file_path in glob.glob(pattern):
                    try:
                        if os.path.isfile(file_path):
                            file_age = time.time() - os.path.getmtime(file_path)
                            if file_age > 3600:  # 1 hour
                                os.remove(file_path)
                                logger.debug(f"Removed old temp file: {file_path}")
                    except Exception as e:
                        logger.debug(f"Could not remove temp file {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error cleaning temp files: {e}")
    
    def _cleanup_old_logs(self):
        """Clean up old log files"""
        try:
            import glob
            from datetime import datetime, timedelta
            
            log_dir = '/app/logs'
            if not os.path.exists(log_dir):
                return
            
            # Remove log files older than 7 days
            cutoff_time = time.time() - (7 * 24 * 3600)
            
            for log_file in glob.glob(os.path.join(log_dir, '*.log*')):
                try:
                    if os.path.isfile(log_file) and os.path.getmtime(log_file) < cutoff_time:
                        os.remove(log_file)
                        logger.debug(f"Removed old log file: {log_file}")
                except Exception as e:
                    logger.debug(f"Could not remove log file {log_file}: {e}")
        except Exception as e:
            logger.error(f"Error cleaning old logs: {e}")
    
    def log_resource_stats(self, stats: Dict):
        """Log current resource statistics"""
        logger.info(f"Resource Stats - Memory: {stats.get('memory_percent', 0):.1f}% "
                   f"({stats.get('memory_used_gb', 0):.1f}GB used, "
                   f"{stats.get('memory_available_gb', 0):.1f}GB available), "
                   f"CPU: {stats.get('cpu_percent', 0):.1f}%, "
                   f"FDs: {stats.get('file_descriptors', 0)}, "
                   f"Connections: {stats.get('connections', 0)}, "
                   f"Processes: {stats.get('process_count', 0)}")
    
    def run(self):
        """Main monitoring loop"""
        logger.info("Starting resource monitor...")
        
        while self.running:
            try:
                # Get current stats
                stats = self.get_system_stats()
                if not stats:
                    time.sleep(60)
                    continue
                
                # Log stats
                self.log_resource_stats(stats)
                
                # Check thresholds
                warnings = self.check_resource_thresholds(stats)
                if warnings:
                    logger.warning(f"Resource warnings: {'; '.join(warnings)}")
                
                # Perform cleanup if needed
                current_time = time.time()
                should_cleanup = (
                    warnings or  # Cleanup if thresholds exceeded
                    (current_time - self.last_cleanup) > self.cleanup_interval  # Regular cleanup
                )
                
                if should_cleanup:
                    self.perform_cleanup()
                    self.last_cleanup = current_time
                
                # Sleep for 60 seconds
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)
        
        logger.info("Resource monitor stopped")

def main():
    """Main entry point"""
    monitor = ResourceMonitor()
    try:
        monitor.run()
    except KeyboardInterrupt:
        logger.info("Resource monitor interrupted by user")
    except Exception as e:
        logger.error(f"Resource monitor failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
