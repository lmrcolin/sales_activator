import time
import random
from typing import Optional
import requests

class Http:
    def __init__(self, user_agent: str, delay: float = 1.0):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.delay = delay

    def get(self, url: str, timeout: int = 15) -> Optional[requests.Response]:
        try:
            resp = self.session.get(url, timeout=timeout)
            time.sleep(self.delay + random.random() * 0.5)
            if resp.status_code == 200:
                return resp
        except requests.RequestException:
            return None
        return None
