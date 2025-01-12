import time
import requests
import sys
from colorama import Fore, init

init()
start = time.time()

url = "http://127.0.0.1:8000/get"
files = {"file": open("test.wav.txt", "r").read()}

try:
    response = requests.post(url, json=files)
    print(Fore.GREEN + "=========== GET PASS ============")
    print(response.json())
    print(Fore.GREEN + "=================================")
except Exception as e:
    print(Fore.RED + "=========== GET PASS ============")
    print(e)
    print(Fore.RED + "=================================")
    
end = time.time()

print(Fore.YELLOW + f"\nRuntime: {end - start}")