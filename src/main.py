from dotenv import load_dotenv
import os
import requests

load_dotenv('.env')

WALKSCORE_KEY = os.environ.get('WALKSCORE_KEY')

def get_walkscore(lat: float, lon: float):
    response = requests.get(f'https://api.walkscore.com/score?format=json&lat={lat}&lon={lon}&transit=1&bike=1&wsapikey={WALKSCORE_KEY}')
    if response.ok:
        return response.json()
    return

print(get_walkscore(38.328732, -85.764771))