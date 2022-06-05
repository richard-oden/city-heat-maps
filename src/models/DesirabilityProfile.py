from models.DesirabilityFactor import DesirabilityFactor

class DesirabilityProfile():
    def __init__(
        self, 
        income: DesirabilityFactor | None,
        rent_per_bd: DesirabilityFactor | None,
        home_value: DesirabilityFactor | None,
        transit_importance: float | None,
        walking_importance: float | None,
        biking_importance: float | None,
        commute_time: DesirabilityFactor | None,
        population_density: DesirabilityFactor | None,
        housing_availability: DesirabilityFactor | None,
        age: DesirabilityFactor | None,
        sex_ratio: DesirabilityFactor | None, 
        racial_diversity: DesirabilityFactor | None,
        predominant_race: DesirabilityFactor | None,
        education_level: DesirabilityFactor | None,
        unemployment_rate: DesirabilityFactor | None,
        family_ratio: DesirabilityFactor | None):

        self.income = income
        self.rent_per_bd = rent_per_bd
        self.home_value = home_value
        self.transit_importance = transit_importance
        self.walking_importance = walking_importance
        self.biking_importance = biking_importance
        self.commute_time = commute_time
        self.population_density = population_density
        self.housing_availability = housing_availability
        self.age = age
        self.sex_ratio = sex_ratio 
        self.racial_diversity = racial_diversity
        self.predominant_race = predominant_race
        self.education_level = education_level
        self.unemployment_rate = unemployment_rate
        self.family_ratio =  family_ratio