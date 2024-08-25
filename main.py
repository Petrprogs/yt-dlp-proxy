import requests
import os
import io
import time
import sys
import subprocess
import json

def get_proxies():
    request = requests.get("https://nnp.nnchan.ru/mahoproxy.php?u=https://api.sandvpn.com/fetch-free-proxys")
    print(request.text)
    if request.status_code == 200:
        return request.json()
    else:
        request.raise_for_status()
        

def get_best_proxy(proxy_json):
    proxy_times = []
    proxy_json1 = proxy_json
    for i, item in enumerate(proxy_json):
        if item["host"] != "" and item["country"] != "Russia":
            proxy_str = ""
            print(f'Testing {item["host"]}:{item["port"]}')
            if item["username"]:
                proxy_str = f'{item["username"]}:{item["password"]}@{item["host"]}:{item["port"]}'
            else:
                proxy_str = f'{item["host"]}:{item["port"]}'
            url = "http://212.183.159.230/5MB.zip"
            with io.BytesIO() as f:
                start = time.perf_counter()
                try:
                    r = requests.get(url, stream=True, proxies={"http": proxy_str}, timeout=20)
                except:
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
                            start = 500
                            break 
                        sys.stdout.write("\r[%s%s] %s Mbps" % ('=' * done, ' ' * (30-done), dl//(time.perf_counter() -
                        start) / 100000))
                else:
                    del proxy_json[i]
                    continue
            #print( f"\n10MB = {(time.perf_counter() - start):.2f} seconds")
                item.update({"time": round(time.perf_counter() - start, 2)})
                proxy_times.append(item)
            
        else:
            del proxy_json[i]
    print(proxy_times)
    min_value = min([item["time"] for item in proxy_times])
    print(min_value)
    for item in proxy_times:
      if item["time"] == min_value:
        return item

def update_proxies():
  proxy_json = get_proxies()
  best_proxy_json = get_best_proxy(proxy_json)
  with open(os.path.abspath(__file__).split("main.py")[0]+"proxy.json", "w") as f:
    f.write(json.dumps(best_proxy_json, indent=4))
    
def run_yt_dlp():
  proxy_url = ""
  with open(os.path.abspath(__file__).split("main.py")[0]+"proxy.json", "r") as f:
    proxy_dict = json.load(f)
    if proxy_dict["username"]:
      proxy_url = f'{proxy_dict["username"]}:{proxy_dict["password"]}@{proxy_dict["host"]}:{proxy_dict["port"]}'
    else:
      proxy_url = f'{proxy_dict["host"]}:{proxy_dict["port"]}'
  args = ["/bin/yt-dlp", "--proxy", proxy_url]+[str(arg) for arg in sys.argv]
  subprocess.run(args)

def main():
  if "update" in sys.argv:
    update_proxies()
  elif len(sys.argv) == 1:
    print("usage: main.py update | <yt-dlp args> \n\nScript for starting yt-dlp with best free proxy\n\nCommands:\n update   Update best proxy\n")
  else:
    sys.argv.pop(0)
    run_yt_dlp()

main()
