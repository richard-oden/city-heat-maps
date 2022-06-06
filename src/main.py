
from dotenv import load_dotenv
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from uszipcode import ComprehensiveZipcode
import helpers.zipcode_helper as zipcode_helper
import os
import matplotlib.pyplot as plt
import numpy as np
import requests

load_dotenv('.env')

WALKSCORE_KEY = os.environ.get('WALKSCORE_KEY')

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


zipcodes = zipcode_helper.get_comprehensive_zipcodes('San Francisco', 'California')
percentage = zipcode_helper.get_transit_mode_percentage(zipcodes[0], zipcode_helper.transit_modes[0])

# zipcode_samples = {zipcode:sample_coordinates_within_zipcode(zipcode, 0.01) for zipcode in zipcodes}

# for zipcode,samples in zipcode_samples.items():
#     polygon = try_polygon(zipcode.polygon)
#     if polygon:
#         plt.plot(*polygon.exterior.xy)

# plt.gca().axis("equal")
# plt.show()
# print('done')