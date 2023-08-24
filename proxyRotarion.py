import threading
import requests
import pathlib
import signal
from math import ceil

parent_dir = pathlib.Path(__file__).parent.resolve()
proxies_file = str(parent_dir)+'/proxies.txt'
failed_proxies_file = str(parent_dir)+'/failed_proxies.txt'
used_proxies_file = str(parent_dir)+'/used_proxies.txt'
request_timeout = 30
failed_proxies_arr = []
used_proxies_arr = []
unused_proxies_arr = []

running_flags = [True]
threads = []

sites_to_check = [
    "https://4.ident.me",
    "https://4.ident.me",
    "https://4.ident.me",
    "https://4.ident.me",
    "https://4.ident.me",
    "https://4.ident.me",
    "https://4.ident.me"
]


def chunk_into_n(lst, n):
    size = ceil(len(lst) / n)
    return list(
        map(lambda x: lst[x * size:x * size + size],
            list(range(n)))
    )

def make_request(idx, proxies):
    site = sites_to_check[idx]
    succeed = False
    for proxy in proxies:
        if not succeed and running_flags[idx]:
            print(proxy + " | " + str(idx))
            try:
                res = requests.get(
                    site, timeout=request_timeout, proxies={"http": proxy, "https": proxy})
                print(f"Using the proxy: {proxy} --> {res.text}")
                used_proxies_arr.append(proxy)
                succeed = True
                continue
            except requests.exceptions.RequestException:
                print("F")
                failed_proxies_arr.append(proxy)
                continue  # Move to the next proxy
        else:
            unused_proxies_arr.append(proxy)

def signal_handler(sig, frame):
    request_timeout = 1
    for index in range(len(running_flags)):
        print(f"Ctrl+C detected. Stopping thread {index}...")
        running_flags[index] = False
        
def safe_arr_in_file(arr, filename, mode):
    with open(filename, mode) as txt_file:
        for line in arr:
            txt_file.write(line + "\n")

signal.signal(signal.SIGINT, signal_handler)

with open(proxies_file, "r") as f:
    proxies = f.read().split("\n")
    proxy_chunks = chunk_into_n(proxies, len(sites_to_check))
    running_flags *= len(proxy_chunks)

    for idx, proxy_chunk in enumerate(proxy_chunks):
        thread = threading.Thread(target=make_request, args=(idx, proxy_chunk))
        thread.start()
        threads.append(thread)

try:
    for thread in threads:
        thread.join(timeout=1)
except KeyboardInterrupt:
    print("Main thread detected Ctrl+C. Waiting for the threads to exit...")


# Clean up
for thread in threads:
    thread.join()


safe_arr_in_file(failed_proxies_arr, failed_proxies_file, "a")
safe_arr_in_file(used_proxies_arr, used_proxies_file, "a")
safe_arr_in_file(unused_proxies_arr, proxies_file, "w")

print("All threads have exited.")