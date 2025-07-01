import requests
from .config import settings
import socket
import logging


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

    def get(self, endpoint, params=None, headers=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        merged_headers = self.default_headers.copy()
        if headers:
            merged_headers.update(headers)
        try:
            response = requests.get(url, params=params, headers=merged_headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def post(self, endpoint, data=None, json=None, headers=None):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        merged_headers = self.default_headers.copy()
        if headers:
            merged_headers.update(headers)
        try:
            response = requests.post(url, data=data, json=json, headers=merged_headers, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            if data and data.get("nodeToken"):
                settings.SRV_API_KEY = data.get("nodeToken").get("access_token")
            return data
        except Exception as e:
            return {"error": str(e)}


class MinerClient(HttpClient):
    def __init__(self, timeout=10):
        token = settings.SRV_API_KEY
        super().__init__(settings.SRV_API_URL, timeout, authorization=f"Bearer {token}")

class ValidatorClient(HttpClient):
    def __init__(self, timeout=10):
        token = settings.SRV_API_KEY
        super().__init__(settings.SRV_API_URL, timeout, authorization=f"Bearer {token}")