from math import floor
from sqlalchemy import Column
from uszipcode import SearchEngine
from uszipcode import ComprehensiveZipcode


transit_modes = [
    'Car, Truck, Or Van',
    'Public Transportation',
    'Taxicab',
    'Motorcycle',
    'Bicycle, Walked, Or Other Means'
]

def get_column_data_values(column: Column) -> list:
    if column is None:
        return

    return next((a['values'] for a in column if a['key'] == 'Data'), None)

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
    '''
    Returns age bracket index based on the supplied age.
    '''
    if age < 0:
        return 0

    bracket_index = floor(float(age)/5)
    if bracket_index > 17:
        return 17

    return bracket_index


def get_age_percentage(zipcode: ComprehensiveZipcode, desired_age: int) -> float | None:
    '''
    Returns the percentage of inhabitants in the same bracket as desired_age.
    '''
    age_responses = next((pba['values'] for pba in zipcode.population_by_age if pba['key'] == 'Total'), None)
    if age_responses is None:
        return

    age_bracket = get_age_bracket(desired_age)
    desired_age_responses = next((ar['y'] for ar in age_responses if ar['x'] == age_bracket), None)
    if desired_age_responses is None:
        return

    total_responses = sum([ar['y'] for ar in age_responses])
    return desired_age_responses / total_responses
    

def get_rent_per_bd_percentage(zipcode: ComprehensiveZipcode, desired_rent_per_bd: int) -> float | None:
    '''
    Returns the percentage of bedrooms that are in the same bracket or less than desired_rent_per_bd.
    '''

    def get_rent_bracket(rent: int | float) -> int:
        '''
        Returns rent bracket index based on the supplied rent.
        '''
        if rent <= 0:
            return 0

        bracket_index = floor(float(rent)/200)
        if bracket_index > 5:
            return 5

        return bracket_index

    def get_rent_responses(column: Column, multiplier: float | int) -> dict:
        '''
        Returns a dict containing desired and total rent responses given the column and multiplier (number of bedrooms).
        '''
        responses = get_column_data_values(column)
        if responses is None:
            return { 'desired': 0, 'total': 0 }
        
        bracket = get_rent_bracket(desired_rent_per_bd * multiplier)
        desired_responses = sum([r['y'] for r in responses if responses.index(r) <= bracket]) * desired_rent_per_bd
        total_responses = sum([r['y'] for r in responses]) * desired_rent_per_bd

        return { 'desired': round(desired_responses), 'total': round(total_responses) }

    rent_responses = [
        get_rent_responses(zipcode.monthly_rent_including_utilities_studio_apt, 0.5), # For simplicity, studios will be considered as having .5 bedrooms.
        get_rent_responses(zipcode.monthly_rent_including_utilities_1_b, 1),
        get_rent_responses(zipcode.monthly_rent_including_utilities_2_b, 2),
        get_rent_responses(zipcode.monthly_rent_including_utilities_3plus_b, 3.5) # For simplicity, 3+ bedroom rentals will be considered as having 3.5 bedrooms.
    ]

    total_responses = sum([r['total'] for r in rent_responses])
    if total_responses is 0:
        return

    desired_responses = sum([r['desired'] for r in rent_responses])

    return  desired_responses / total_responses 