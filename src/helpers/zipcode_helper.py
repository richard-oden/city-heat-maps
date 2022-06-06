from math import floor
from uszipcode import SearchEngine
from uszipcode import ComprehensiveZipcode


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