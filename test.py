import requests

BASE = "https://127.0.0.1:5000/appointment/"

response = requests.put(BASE + "DioPorco")
print(response.json())