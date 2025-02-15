import requests
from proxy_provider import ProxyProvider

class VNNetProvider(ProxyProvider):
    """
    Fetch proxies from VNNet browser extension
    """
    PROXIES_LIST_URL = "https://poteto.ru/servers.json"

    def fetch_proxies(self):
        """Fetch proxies from SandVPN."""
        response = requests.get(self.PROXIES_LIST_URL, timeout=10)
        response.raise_for_status()
        response_json = response.json()
        return_list = []
        for proxy in response_json:
            return_list.append(
                {
                    "city": "Unknown city",
                    "country": proxy["name"],
                    "host": proxy["proxy_host"],
                    "port": proxy["proxy_port"],
                    "username":  proxy["proxy_user"],
                    "password":  proxy["proxy_pass"]
                }
            )
        return return_list