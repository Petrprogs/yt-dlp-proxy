import requests
import random
import os
import io
import time
import sys
import subprocess
import json
import importlib
import inspect
from concurrent.futures import ThreadPoolExecutor, as_completed
from proxy_provider import ProxyProvider
from proxy_providers import *
from tqdm import tqdm

SPEEDTEST_URL = "http://212.183.159.230/5MB.zip"

def is_valid_proxy(proxy):
    """Check if the proxy is valid."""
    return proxy.get("host") is not None and proxy.get("country") != "Russia"


def construct_proxy_string(proxy):
    """Construct a proxy string from the proxy dictionary."""
    if proxy.get("username"):
        return (
            f'{proxy["username"]}:{proxy["password"]}@{proxy["host"]}:{proxy["port"]}'
        )
    return f'{proxy["host"]}:{proxy["port"]}'


def test_proxy(proxy):
    """Test the proxy by measuring the download time."""
    proxy_str = construct_proxy_string(proxy)
    start_time = time.perf_counter()
    try:
        response = requests.get(
            SPEEDTEST_URL,
            stream=True,
            proxies={"http": f"http://{proxy_str}"},
            timeout=5,
        )
        response.raise_for_status()  # Ensure we raise an error for bad responses

        total_length = response.headers.get("content-length")
        if total_length is None or int(total_length) != 5242880:
            return None

        with io.BytesIO() as f:
            download_time, _ = download_with_progress(
                response, f, total_length, start_time
            )
            return {"time": download_time, **proxy}  # Include original proxy info
    except requests.RequestException:
        return None


def download_with_progress(response, f, total_length, start_time):
    """Download content from the response with progress tracking."""
    downloaded_bytes = 0
    for chunk in response.iter_content(1024):
        downloaded_bytes += len(chunk)
        f.write(chunk)
        done = int(30 * downloaded_bytes / int(total_length))
        if done == 6:
            break
        if (
            done > 3
            and (downloaded_bytes // (time.perf_counter() - start_time) / 100000) < 1.0
        ):
            return float("inf"), downloaded_bytes
    return round(time.perf_counter() - start_time, 2), downloaded_bytes


def save_proxies_to_file(proxies, filename="proxy.json"):
    """Save the best proxies to a JSON file."""
    with open(os.path.join(os.path.dirname(__file__), filename), "w") as f:
        json.dump(proxies, f, indent=4)


def get_best_proxies(providers):
    """Return the top five proxies based on speed from all providers."""
    all_proxies = []
    proxies = None
    for provider in providers:
        try:
            print(f"Fetching proxies from {provider.__class__.__name__}")
            proxies = provider.fetch_proxies()
            all_proxies.extend([proxy for proxy in proxies if is_valid_proxy(proxy)])
        except Exception as e:
            print(f"Failed to fetch proxies from {provider.__class__.__name__}: {e}")

    best_proxies = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {executor.submit(test_proxy, proxy): proxy for proxy in all_proxies}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Testing proxies", bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_noinv_fmt}]", unit=' proxies', unit_scale=True, ncols=80):
            result = future.result()
            if result is not None:
                best_proxies.append(result)
    return sorted(best_proxies, key=lambda x: x["time"])[:5]


def update_proxies():
    """Update the proxies list and save the best ones."""
    providers = []
    for filename in os.listdir(os.path.join(os.path.dirname(__file__), "proxy_providers")):
        # Check if the file is a Python module
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]  # Remove the '.py' suffix
            module_path = f'{"proxy_providers"}.{module_name}'
            module = importlib.import_module(module_path)
            classes = inspect.getmembers(module, inspect.isclass)
            providers.append(
                [classs[-1]() for classs in classes if classs[0] != "ProxyProvider"][0]
            )
    print(providers)
    best_proxies = get_best_proxies(providers)
    save_proxies_to_file(best_proxies)
    print("All done.")


def run_yt_dlp():
    """Run yt-dlp with a randomly selected proxy."""
    while True:
        with open("proxy.json", "r") as f:
            proxy = random.choice(json.load(f))
            proxy_str = construct_proxy_string(proxy)
            print(f"Using proxy from {proxy['city']}, {proxy['country']}")

            if execute_yt_dlp_command(proxy_str):
                break  # Exit loop if command was successful
            print("Got 'Sign in to confirm' error. Trying again with another proxy...")


def execute_yt_dlp_command(proxy_str):
    """Execute the yt-dlp command with the given proxy."""
    command = f"yt-dlp --color always --proxy http://{proxy_str} {' '.join([str(arg) for arg in sys.argv])} 2>&1 | tee tempout"
    subprocess.run(command, shell=True)
    with open("tempout", "r") as log_fl:
        log_text = log_fl.read()
        return "Sign in to" not in log_text and "403" not in log_text


def main():
    """Main function to handle script arguments and execute the appropriate command."""
    try:
        if "update" in sys.argv:
            update_proxies()
        elif len(sys.argv) < 2:
            print(
                "usage: main.py update | <yt-dlp args> \nScript for starting yt-dlp with best free proxy\nCommands:\n update   Update best proxy"
            )
        else:
            sys.argv.pop(0)
            run_yt_dlp()
    except KeyboardInterrupt:
        print("Canceled by user")


if __name__ == "__main__":
    main()
