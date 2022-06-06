from math import floor
from statistics import mode
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


def get_bracket_index(value: int | float, interval: int, max_bracket: int) -> int:
    '''
    Returns bracket index of value based on interval and max_bracket.
    '''
    if value <= 0:
        return 0

    bracket_index = floor(float(value)/interval)
    if bracket_index > max_bracket:
        return max_bracket

    return bracket_index


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


def get_age_percentage(zipcode: ComprehensiveZipcode, desired_age: int) -> float | None:
    '''
    Returns the percentage of inhabitants in the same bracket as desired_age.
    '''
    age_responses = next((pba['values'] for pba in zipcode.population_by_age if pba['key'] == 'Total'), None)
    if age_responses is None:
        return

    age_bracket = get_bracket_index(desired_age, 5, 17)
    desired_age_responses = next((ar['y'] for ar in age_responses if ar['x'] == age_bracket), None)
    if desired_age_responses is None:
        return

    total_responses = sum([ar['y'] for ar in age_responses])
    return desired_age_responses / total_responses
    

def get_rent_per_bd_percentage(zipcode: ComprehensiveZipcode, desired_rent_per_bd: int) -> float | None:
    '''
    Returns the percentage of bedrooms that are in the same bracket or less than desired_rent_per_bd.
    '''
    def get_rent_responses(column: Column, multiplier: float | int) -> dict:
        '''
        Returns a dict containing desired and total rent responses given the column and multiplier (number of bedrooms).
        '''
        responses = get_column_data_values(column)
        if responses is None:
            return { 'desired': 0, 'total': 0 }
        
        bracket = get_bracket_index(desired_rent_per_bd * multiplier, 200, 5)
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


def get_commute_time_percentage(zipcode: ComprehensiveZipcode, desired_commute_time_minutes: int) -> float | None:
    '''
    Returns percentage of commute times that are less than or in the same bracket as desired_commute_time_minutes.
    '''
    responses = get_column_data_values(zipcode.travel_time_to_work_in_minutes)
    if responses is None:
        return
    
    bracket = get_bracket_index(desired_commute_time_minutes, 10, 7)
    desired_responses = sum([r['y'] for r in responses if responses.index(r) <= bracket])
    total_responses = sum([r['y'] for r in responses])

    return desired_responses / total_responses


def get_available_housing_percentage(zipcode: ComprehensiveZipcode, desired_housing_availability: float) -> float | None:
    '''
    Returns a percentage representing how close the zipcode's housing availability is to desired_housing_availabilibility.
    '''
    if zipcode.housing_units is None or zipcode.occupied_housing_units is None:
        return

    housing_availability = 1 - (zipcode.occupied_housing_units / zipcode.housing_units)
    return desired_housing_availability / housing_availability


def get_sex_ratio_percentage(zipcode: ComprehensiveZipcode, desired_sex_ratio: float) -> float | None:
    '''
    Returns a percentage representing how close the zipcode's ratio of males to females is to desired_sex_ratio.
    '''
    responses = get_column_data_values(zipcode.population_by_gender)
    if responses is None:
        return
    
    male_responses = next((r['y'] for r in responses if r['x'] == 'Male'), None)
    female_responses = next((r['y'] for r in responses if r['x'] == 'Female'), None)

    if male_responses is None or female_responses is None:
        return
    
    sex_ratio = male_responses / female_responses
    return desired_sex_ratio / sex_ratio


def get_diversity_percentage(zipcode: ComprehensiveZipcode, desired_diversity: float) -> float | None:
    '''
    Returns a percentage representing how close the zipcode's diversity is to desired_diversity.
    '''
    responses = get_column_data_values(zipcode.population_by_race)
    if responses is None:
        return

    total_responses = sum([r['y'] for r in responses])
    percentage_responses_by_race = [r['y'] / total_responses for r in responses]
    diversity = mode(percentage_responses_by_race)
    return desired_diversity / diversity
