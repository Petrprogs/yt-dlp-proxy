import requests
from proxy_provider import ProxyProvider

class SandVPNProvider(ProxyProvider):
    """
    Fetch proxies from SandVPN browser extension
    """
    PROXIES_LIST_URL = "https://api.sandvpn.com/fetch-free-proxys"

    def fetch_proxies(self):
        """Fetch proxies from SandVPN."""
        response = requests.get(self.PROXIES_LIST_URL, timeout=10)
        response.raise_for_status()
        return response.json()