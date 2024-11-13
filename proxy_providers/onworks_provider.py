import requests
from proxy_provider import ProxyProvider

class VPNOnlineProvider(ProxyProvider):
    """
    Fetch proxies from VPNOnline browser extension
    """
    PROXIES_LIST_URL = "https://www.onworks.net/vpn.json?v=07"

    def fetch_proxies(self):
        """Fetch proxies from SandVPN."""
        response = requests.get(self.PROXIES_LIST_URL, timeout=5)
        response.raise_for_status()
        response_json = response.json()
        return_list = []
        for server in response_json["data"]["servers"]["10501"]["proxies"]:
            return_list.append(
                {
                    "city": "Unknown city",
                    "country": server["country"].upper(),
                    "host": server["proxy"].split(":")[0],
                    "port": server["proxy"].split(":")[1],
                    "username": response_json["data"]["servers"]["10501"]["credentials"]["username"],
                    "password": response_json["data"]["servers"]["10501"]["credentials"]["password"]
                }
            )
        return return_list
