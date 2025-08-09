## yt-dlp-proxy Guide

yt-dlp-proxy is a script designed to help you avoid throttling and bans by automatically selecting the best proxy for yt-dlp. 

## Quick Start

### Option 1: Use the Python Script (Development)
```bash
python3 main.py
```

### Option 2: Build and install binary (Recommended)

```bash
make build
make install
```

## Usage

#### Update proxy list
```bash
yt-dlp-proxy update
```

This will also perform a speed test for each free proxy and select the best one available.

By default, yt-dlp-proxy uses only two parallel threads to test the proxy, but using the `--max-workers` parameter, you can set the desired number of worker threads to speed up proxy testing. Before setting this parameter, make sure that your Internet bandwidth allows you to do this.

```bash
yt-dlp-proxy update --max-workers 10
```

#### Download with yt-dlp-proxy
Use yt-dlp-proxy just like you would use yt-dlp! Pass all the arguments to yt-dlp-proxy instead.
Example:

```bash
yt-dlp-proxy --format bv[vcodec^=avc!]+ba https://www.youtube.com/watch?v=bQB0_4BG-9F
```

If the proxy becomes slow over time, rerun the update command to refresh the proxy selection.


### Creating custom proxy providers

First you need to create new py module in proxy_providers directory using this code template:
```
import requests
from proxy_provider import ProxyProvider

class SomeProxyProvider(ProxyProvider):
    """
    Someproxy provider
    """
    PROXIES_LIST_URL = "https://goodproxies.net/list.json"

    def fetch_proxies(self):
        """Fetch proxies from goodproxies.net"""
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
```
As you can see, this script uses one json structure for all providers. In example code we've "converted" json response from server to python dictionary, compatible with yt-dlp-proxy. Here is basic example of json structure yt-dlp-proxy uses:
```
[
  {
    "city": "City1",
    "country": "Country1",
    "host": "0.0.0.0",
    "password": "password123",
    "port": "proxy_port",
    "username": "squid_username"
  }
]
```
Please note that all proxy providers are loaded automatically and you don't need to import them manually in ```main.py```

