from math import floor
from dotenv import load_dotenv
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from uszipcode import SearchEngine
from uszipcode import ComprehensiveZipcode
import os
import matplotlib.pyplot as plt
import numpy as np
import requests

load_dotenv('.env')

WALKSCORE_KEY = os.environ.get('WALKSCORE_KEY')

transit_modes = [
    'Car, Truck, Or Van',
    'Public Transportation',
    'Taxicab',
    'Motorcycle',
    'Bicycle, Walked, Or Other Means'
]

def get_comprehensive_zipcodes(city: str, state: str) -> list:
    with SearchEngine(simple_or_comprehensive=SearchEngine.SimpleOrComprehensiveArgEnum.comprehensive) as search:
        return search.by_city_and_state(city=city, state=state, returns=None)

def get_transit_mode_percentage(zipcode: ComprehensiveZipcode, desired_transit_mode: str) -> float | None:
    transit_mode_responses = zipcode.means_of_transportation_to_work_for_workers_16_and_over[0]['values']
    desired_transit_mode_responses = next((tm['y'] for tm in transit_mode_responses if tm['x'] == desired_transit_mode), None)
    if desired_transit_mode_responses is None:
        return

    total_responses = sum([tm['y'] for tm in transit_mode_responses])
    return desired_transit_mode_responses / total_responses

def get_age_bracket(age: int) -> int:
    if age < 0:
        return 0

    bracket_index = floor(float(age)/5)
    if bracket_index > 17:
        return 17

    return bracket_index

def get_age_percentage(zipcode: ComprehensiveZipcode, desired_age: int) -> float | None:
    age_responses = next((pba['values'] for pba in zipcode.population_by_age if pba['key'] == 'Total'), None)
    if age_responses is None:
        return

    age_bracket = get_age_bracket(desired_age)
    desired_age_responses = next((ar['y'] for ar in age_responses if ar['x'] == age_bracket), None)
    if desired_age_responses is None:
        return

    total_responses = sum([ar['y'] for ar in age_responses])
    return desired_age_responses / total_responses

def try_polygon(coords: (list|tuple)) -> Polygon | None:
    try:
        if not coords:
            return
        return Polygon(coords if len(coords) > 1 else coords[0])
    except:
        return


def sample_coordinates_within_zipcode(zipcode: ComprehensiveZipcode, interval: float):
    polygon = try_polygon(zipcode.polygon)
    if not polygon:
        return [Point(zipcode.lat, zipcode.lng)]

    lat_min, lng_min, lat_max, lng_max = polygon.bounds

    points = []
    for lat in np.arange(lat_min, lat_max, interval):
        for lon in np.arange(lng_min, lng_max, interval):
            point = Point(lat, lon)
            if polygon.contains(point):
                points.append(point)
                
    if not len(points):
        return [Point(zipcode.lat, zipcode.lng)]

    return points


def get_walkscore(lat: float, lng: float) -> dict:
    response = requests.get(f'https://api.walkscore.com/score?format=json&lat={lat}&lon={lng}&transit=1&bike=1&wsapikey={WALKSCORE_KEY}')
    if response.ok:
        return response.json()
    return


zipcodes = get_comprehensive_zipcodes('Portland', 'Oregon')
percentage = get_age_percentage(zipcodes[0], 29)

# zipcode_samples = {zipcode:sample_coordinates_within_zipcode(zipcode, 0.01) for zipcode in zipcodes}

# for zipcode,samples in zipcode_samples.items():
#     polygon = try_polygon(zipcode.polygon)
#     if polygon:
#         plt.plot(*polygon.exterior.xy)

# plt.gca().axis("equal")
# plt.show()