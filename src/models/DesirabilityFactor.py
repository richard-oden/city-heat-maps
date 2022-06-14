class DesirabilityFactor():
    def __init__(self, value: float, importance: float):
        if value > 1 or value < 0:
            raise ValueError(f'Value must be between 0 and 1. Current: {value}')

        if importance > 1 or importance < 0:
            raise ValueError(f'Importance must be between 0 and 1. Current: {importance}')

        self.value = value
        self.importance = importance
        self.score = value * importance