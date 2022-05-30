from dotenv import load_dotenv
from uszipcode import SearchEngine
import os
import requests

load_dotenv('.env')

WALKSCORE_KEY = os.environ.get('WALKSCORE_KEY')

def get_zipcodes_by_city(city: str, state: str) -> list:
    with SearchEngine() as search:
        results = search.by_city_and_state(city='Louisville', state='Kentucky', returns=None)
        return [int(result.zipcode) for result in results]

def get_walkscore(lat: float, lon: float):
    response = requests.get(f'https://api.walkscore.com/score?format=json&lat={lat}&lon={lon}&transit=1&bike=1&wsapikey={WALKSCORE_KEY}')
    if response.ok:
        return response.json()
    return

print(get_zipcodes_by_city('Louisville', 'Kentucky'))
print(get_walkscore(38.328732, -85.764771))