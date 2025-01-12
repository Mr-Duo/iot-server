import time
import requests
import sys
from colorama import Fore, init

init()
start = time.time()

url = "http://127.0.0.1:8000/add"
files = {"name": "Dương", "file": open("test.wav.txt", "r").read()}
try:
    response = requests.post(url, json=files)
    print(Fore.GREEN + "========== POST PASS ============")
    print(response.json())
    print(Fore.GREEN + "=================================")
except Exception as e:
    print(Fore.RED + "========== POST PASS ============")
    print(e)
    print(Fore.RED + "=================================")
    
end = time.time()

print(Fore.YELLOW + f"\nRuntime: {end - start}")