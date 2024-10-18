import requests
import random
import os
import io
import time
import sys
import subprocess
import json

PROXIES_LIST = "https://nnp.nnchan.ru/mahoproxy.php?u=https://api.sandvpn.com/fetch-free-proxys"
SPEEDTEST_URL = "http://212.183.159.230/5MB.zip"

def get_proxies():
    request = requests.get(PROXIES_LIST)
    if request.status_code == 200:
        return request.json()
    else:
        request.raise_for_status()
        

def get_best_proxy(proxy_json):
    proxy_times = []
    for i, item in enumerate(proxy_json):
        if item["host"] != "" and item["country"] != "Russia":
            proxy_str = ""
            print(f'Testing {item["host"]}:{item["port"]}')
            if item["username"]:
                proxy_str = f'{item["username"]}:{item["password"]}@{item["host"]}:{item["port"]}'
            else:
                proxy_str = f'{item["host"]}:{item["port"]}'
            with io.BytesIO() as f:
                start = time.perf_counter()
                try:
                    r = requests.get(SPEEDTEST_URL, stream=True, proxies={"http": proxy_str}, timeout=20)
                except:
                    print("Proxy is dead, skiping...")
                    del proxy_json[i]
                    continue
                total_length = r.headers.get('content-length')
                dl = 0
                if total_length is None: # no content length header
                    print("no content")
                    f.write(r.content)
                elif int(total_length) == 5242880:
                    for chunk in r.iter_content(1024):
                        dl += len(chunk)
                        f.write(chunk)
                        done = int(30 * dl / int(total_length))
                        if done > 3 and (dl//(time.perf_counter() - start) / 100000) < 1.0:
                            print("\nProxy is too slow, skiping...")
                            start = 500
                            break 
                        sys.stdout.write("\r[%s%s] %s Mbps" % ('=' * done, ' ' * (30-done), dl//(time.perf_counter() -
                        start) / 100000))
                else:
                    del proxy_json[i]
                    continue
                item.update({"time": round(time.perf_counter() - start, 2)})
                proxy_times.append(item)
                print("\n")
            
        else:
            del proxy_json[i]

    best_five_proxies = sorted(proxy_times, key=lambda x: x['time'])[:5]
    return best_five_proxies

def update_proxies():
  proxy_json = get_proxies()
  best_proxy_json = get_best_proxy(proxy_json)
  with open(os.path.abspath(__file__).split("main.py")[0]+"proxy.json", "w") as f:
    f.write(json.dumps(best_proxy_json, indent=4))
  print("All done.")


def run_yt_dlp():
  proxy_url = ""
  error =  True
  while error:
    with open(os.path.abspath(__file__).split("main.py")[0]+"proxy.json", "r") as f:
      proxy_dict = random.choice(json.load(f))
      print(f"Using proxy based in {proxy_dict['city']}, {proxy_dict['country']}")
      if proxy_dict["username"]:
        proxy_url = f'{proxy_dict["username"]}:{proxy_dict["password"]}@{proxy_dict["host"]}:{proxy_dict["port"]}'
      else:
        proxy_url = f'{proxy_dict["host"]}:{proxy_dict["port"]}'
    subprocess.run(f"yt-dlp --color always --proxy  '{proxy_url}' {" ".join([str(arg) for arg in sys.argv])} 2>&1 | tee tempout", shell=True)
    with open("tempout", 'r') as log_fl:
      if 'Sign in to' in  log_fl.readlines()[-1]:
          error = True
          print("Got 'Sign in to confirm' error. Trying again with another proxy...")
      else:
          error = False
  os.remove("tempout") 


def main():
  try:
    if "update" in sys.argv:
      update_proxies()
    elif len(sys.argv) == 1:
      print("usage: main.py update | <yt-dlp args> \n\nScript for starting yt-dlp with best free proxy\n\nCommands:\n update   Update best proxy\n")
    else:
      sys.argv.pop(0)
      run_yt_dlp()
  except KeyboardInterrupt:
    print("Canceled by user")

main()
