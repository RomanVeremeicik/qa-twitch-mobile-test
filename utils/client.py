# utils/client.py
import requests
from typing import Optional

class SimpleClient:
    def __init__(self, base_url: str = "", timeout: int = 10, default_headers: Optional[dict] = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if default_headers:
            self.session.headers.update(default_headers)

    def _url(self, path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base_url}/{path.lstrip('/')}"

    def get(self, path: str, params: dict = None, **kwargs):
        return self.session.get(self._url(path), params=params, timeout=self.timeout, **kwargs)

    def post(self, path: str, json: dict = None, data: dict = None, **kwargs):
        return self.session.post(self._url(path), json=json, data=data, timeout=self.timeout, **kwargs)

    def put(self, path: str, json: dict = None, **kwargs):
        return self.session.put(self._url(path), json=json, timeout=self.timeout, **kwargs)

    def delete(self, path: str, **kwargs):
        return self.session.delete(self._url(path), timeout=self.timeout, **kwargs)

    def close(self):
        try:
            self.session.close()
        except Exception:
            pass
