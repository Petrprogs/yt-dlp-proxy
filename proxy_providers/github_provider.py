import requests
from proxy_provider import ProxyProvider

class GithubProvider(ProxyProvider):
    """
    Fetch proxies from proxifly's Github repo
    """
    PROXIES_LIST_URL = "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.json"

    def fetch_proxies(self):
        """Fetch proxies from proxifly's Github repo"""
        response = requests.get(self.PROXIES_LIST_URL, timeout=10)
        response.raise_for_status()
        response_json = response.json()
        return_list = []
        for proxy in response_json:
            return_list.append(
                {
                    "city": "Unknown city",
                    "country": proxy["geolocation"]["country"],
                    "host": proxy["ip"],
                    "protocol": proxy["protocol"],
                    "port": proxy["port"],
                    "username":  "",
                    "password":  ""
                }
            )
        return return_list