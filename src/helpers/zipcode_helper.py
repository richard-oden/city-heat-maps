from math import floor
from statistics import mode
from sqlalchemy import Column
from uszipcode import SearchEngine
from uszipcode import ComprehensiveZipcode

TRANSPORT_MODE_KEYWORDS = [
    'Car, Truck, Or Van',
    'Public Transportation',
    'Taxicab',
    'Motorcycle',
    'Bicycle, Walked, Or Other Means'
]
MALE_KEYWORD = 'Male'
FEMALE_KEYWORD = 'Female'
EDUCATION_KEYWORDS = [
    'Less Than High School Diploma',
    'High School Graduate',
    'Associate\'s Degree',
    'Bachelor\'s Degree',
    'Master\'s Degree',
    'Professional School Degree',
    'Doctorate Degree'
]
UNEMPLOYED_KEYWORD = 'No Earnings'
FAMILY_KEYWORDS = ['Husband Wife Family Households', 'Single Guardian']
SINGLE_KEYWORDS = ['Singles', 'Singles With Roommate']

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


def get_percentage_comparison(actual_value: int | float, desired_value: int | float) -> float:
    '''
    Returns a percentage representing how similar actual_value and desired_value are, represented as a float between 0 and 1.
    '''
    if actual_value == 0 or desired_value == 0:
        return 0

    if actual_value < desired_value:
        return actual_value / desired_value

    return desired_value / actual_value


def get_comprehensive_zipcodes(city: str, state: str) -> list:
    '''
    Returns a list of uszipcode.ComprehensiveZipCode representing every zipcode in the given city.
    '''
    with SearchEngine(simple_or_comprehensive=SearchEngine.SimpleOrComprehensiveArgEnum.comprehensive) as search:
        return search.by_city_and_state(city=city, state=state, returns=None)
        

def get_transport_mode_percentage(zipcode: ComprehensiveZipcode, desired_transport_mode: str) -> float | None:
    '''
    Returns the percentage of the zipcode's inhabitants aged 16 and over who use the same mode of 
    transport to get to work as desired_transport_mode.
    '''
    if desired_transport_mode not in TRANSPORT_MODE_KEYWORDS:
        return None

    transit_mode_responses = zipcode.means_of_transportation_to_work_for_workers_16_and_over[0]['values']
    desired_transit_mode_responses = next((tm['y'] for tm in transit_mode_responses if tm['x'] == desired_transport_mode), None)
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
    Returns percentage of commute times that are less than or in the same bracket as 
    desired_commute_time_minutes.
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
    Returns a percentage representing how close the zipcode's housing availability is to 
    desired_housing_availability.
    '''
    if zipcode.housing_units is None or zipcode.occupied_housing_units is None:
        return

    housing_availability = 1 - (zipcode.occupied_housing_units / zipcode.housing_units)
    return get_percentage_comparison(housing_availability, desired_housing_availability)


def get_sex_ratio_percentage(zipcode: ComprehensiveZipcode, desired_sex_ratio: float) -> float | None:
    '''
    Returns a percentage representing how close the zipcode's ratio of males to females is to desired_sex_ratio.
    '''
    responses = get_column_data_values(zipcode.population_by_gender)
    if responses is None:
        return
    
    male_responses = next((r['y'] for r in responses if r['x'] == MALE_KEYWORD), None)
    female_responses = next((r['y'] for r in responses if r['x'] == FEMALE_KEYWORD), None)

    if male_responses is None or female_responses is None:
        return
    
    sex_ratio = male_responses / female_responses
    return get_percentage_comparison(sex_ratio, desired_sex_ratio)


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
    return get_percentage_comparison(diversity, desired_diversity)


def get_education_percentage(zipcode: ComprehensiveZipcode, desired_education: str) -> float | None:
    '''
    Returns a percentage representing the zipcode's number of inhabitants aged 25 or over who have the 
    desired level of education.
    '''
    if desired_education not in EDUCATION_KEYWORDS:
        return

    responses = get_column_data_values(zipcode.educational_attainment_for_population_25_and_over)
    if responses is None:
        return

    desired_responses = next((r['y'] for r in responses if r['x'] == desired_education), None)
    if desired_responses is None:
        return
    
    total_responses = sum([r['y'] for r in responses])
    return desired_responses / total_responses


def get_unemployment_percentage(zipcode: ComprehensiveZipcode, desired_unemployment: float) -> float | None:
    '''
    Returns a percentage representing how similar the zipcode's unemployment rate is to desired_unemployment.
    '''
    responses = get_column_data_values(zipcode.employment_status)
    if responses is None:
        return

    unemployed_responses = next((r['y'] for r in responses if r['x'] == UNEMPLOYED_KEYWORD), None)
    if unemployed_responses is None:
        return

    total_responses = sum([r['y'] for r in responses])
    unemployment = unemployed_responses / total_responses
    return get_percentage_comparison(unemployment, desired_unemployment)


def get_family_ratio_percentage(zipcode: ComprehensiveZipcode, desired_family_ratio: float) -> float | None:
    '''
    Returns a percentage representing how similar the zipcode's ratio of families to singles is 
    to desired_family_ratio.
    '''
    responses = get_column_data_values(zipcode.families_vs_singles)
    if responses is None:
        return

    family_responses = [r['y'] for r in responses if r['x'] in FAMILY_KEYWORDS]
    single_responses = [r['y'] for r in responses if r['x'] in SINGLE_KEYWORDS]
    if len(family_responses) == 0 or len(single_responses) == 0:
        return

    family_responses_sum = sum(family_responses)
    single_responses_sum = sum(single_responses)
    family_ratio = family_responses_sum / single_responses_sum
    return get_percentage_comparison(family_ratio, desired_family_ratio)
    