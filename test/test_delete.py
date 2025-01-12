import time
import requests
import sys
from colorama import Fore, init

init()
start = time.time()

url = f"http://127.0.0.1:8000/delete/{sys.argv[1]}"

try:
    response = requests.delete(url)
    print(Fore.GREEN + "=========== GET PASS ============")
    print(response.json())
    print(Fore.GREEN + "=================================")
except Exception as e:
    print(Fore.RED + "=========== GET PASS ============")
    print(e)
    print(Fore.RED + "=================================")
    
end = time.time()

print(Fore.YELLOW + f"\nRuntime: {end - start}")