from dotenv import load_dotenv
from uszipcode import SearchEngine
import os
import requests

load_dotenv('.env')

WALKSCORE_KEY = os.environ.get('WALKSCORE_KEY')

def get_zipcode_coordinates_by_city(city: str, state: str) -> dict:
    with SearchEngine() as search:
        results = search.by_city_and_state(city='Louisville', state='Kentucky', returns=None)
        return {int(result.zipcode): (result.lat, result.lng) for result in results}



def get_walkscore(lat: float, lon: float) -> dict:
    response = requests.get(f'https://api.walkscore.com/score?format=json&lat={lat}&lon={lon}&transit=1&bike=1&wsapikey={WALKSCORE_KEY}')
    if response.ok:
        return response.json()
    return


walkscores = {zipcode:get_walkscore(coordinates[0], coordinates[1])['walkscore'] 
    for (zipcode, coordinates) in get_zipcode_coordinates_by_city('Louisville', 'Kentucky').items()}

print(walkscores)