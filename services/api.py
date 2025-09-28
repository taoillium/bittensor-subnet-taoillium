import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import settings
import socket
from template import __spec_version__ as spec_version
import logging
import atexit
import weakref


logger = logging.getLogger(__name__)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((settings.DETECT_IP, 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

class HttpClient:
    def __init__(self, base_url, timeout=10, authorization=None):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.default_headers = {}
        if authorization:
            self.default_headers['Authorization'] = authorization
        
        # Create session with connection pooling and retry strategy
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
        )
        
        # Configure adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,  # Number of connection pools
            pool_maxsize=20,      # Maximum number of connections in pool
            pool_block=False      # Don't block when pool is full
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Register cleanup function
        atexit.register(self.close)
        
        # Track instances for cleanup
        if not hasattr(HttpClient, '_instances'):
            HttpClient._instances = weakref.WeakSet()
        HttpClient._instances.add(self)

    def get(self, endpoint, params=None, headers=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        merged_headers = self.default_headers.copy()
        if headers:
            merged_headers.update(headers)
        try:
            response = self.session.get(url, params=params, headers=merged_headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"HTTP GET error for {url}: {e}")
            return {"error": str(e)}

    def post(self, endpoint, data=None, json=None, headers=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        merged_headers = self.default_headers.copy()
        if headers:
            merged_headers.update(headers)
        try:
            response = self.session.post(url, data=data, json=json, headers=merged_headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return data
        except Exception as e:
            logger.error(f"HTTP POST error for {url}: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Close the session and all connections"""
        try:
            if hasattr(self, 'session'):
                self.session.close()
                logger.debug("HTTP client session closed")
        except Exception as e:
            logger.error(f"Error closing HTTP client session: {e}")
    
    @classmethod
    def cleanup_all(cls):
        """Cleanup all HttpClient instances"""
        if hasattr(cls, '_instances'):
            for instance in list(cls._instances):
                instance.close()
            cls._instances.clear()


class ServiceApiClient(HttpClient):
    def __init__(self, token:str, timeout=10):
        super().__init__(settings.SRV_API_URL, timeout, authorization=f"Bearer {token}")
