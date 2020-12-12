import random

from collections import Counter

from datetime import datetime
from datetime import timedelta
from copy import deepcopy

# some NPS score weightings that lead to an NPS of around 70
BASE_WEIGHTS = [0.05, 0.045, 0.002, 0.002, 0.002, 0.01, 0.029, 0.05, 0.06, 0.3, 0.45]

# all possible NPS scores
POPULATION = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def flip_coin(probability=0.5):
    weights = [1 - probability, probability]
    dice = random.choices(population=[0, 1], weights=weights)[0]
    return bool(dice)


def adjust_by_x_with_probability(n, adjustment, probability=0.1):
    dice = flip_coin(probability)
    adjustment = adjustment * dice  # tails - no adjustment, heads adjustment
    return n + adjustment


def get_random_date(start, end):
    # https://stackoverflow.com/questions/553303/generate-a-random-date-between-two-other-dates
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)


def generate_random_nps(weights, num_samples=5000, adjust=1, adjust_chance=0.25):
    base_nps = random.choices(
        population=POPULATION,
        weights=weights,
        k=num_samples
    )

    adjusted_nps = []
    for nps in base_nps:
        nps = adjust_by_x_with_probability(nps, adjust, adjust_chance)
        if nps < 0:
            nps = 0
        if nps > 10:
            nps = 10
        adjusted_nps.append(nps)
    return adjusted_nps


def get_adjusted_weights(original_weights, adjustments):
    adjusted = [x + y for x, y in zip(original_weights, adjustments)]
    adjusted = [round(x, 5) for x in adjusted]
    return adjusted


def calculate_nps(scores):
    promoters = 0
    passives = 0
    detractors = 0
    total = len(scores)

    for score in scores:
        if 100.0 >= score > 90.0:
            promoters += 1
        elif 90.0 >= score > 70.0:
            passives += 1
        elif 70.0 >= score > 0.0:
            detractors += 1
        else:
            raise Exception("Invalid NPS Score: {}".format(score))
    nps = (promoters / total) - (detractors / total)
    return [{'y': round((promoters / total) * 100), 'label': 'promoters'},
            {'y': round((passives / total) * 100), 'label': 'passives'},
            {'y': round((detractors / total) * 100), 'label': 'detractors'}]


def calculate_month_score(scores):
    promoters = 0
    passives = 0
    detractors = 0
    total = len(scores)

    for score in scores:
        if 100.0 >= score > 90.0:
            promoters += 1
        elif 90.0 >= score > 70.0:
            passives += 1
        elif 70.0 >= score > 0.0:
            detractors += 1
        else:
            raise Exception("Invalid NPS Score: {}".format(score))
    nps = (promoters / total) - (detractors / total)
    return round(nps * 100)


def calculate_satisfaction_score(scores):
    satisfied = 0
    unsatisfied = 0
    neutral = 0
    very_satisfied = 0
    very_unsatisfied = 0
    total = len(scores)

    for score in scores:
        if 100.0 >= score > 90.0:
            very_satisfied += 1
        elif 90.0 >= score > 80.0:
            satisfied += 1
        elif 80.0 >= score > 70.0:
            neutral += 1
        elif 70.0 >= score > 60.0:
            unsatisfied += 1
        elif 60.0 >= score > 0.0:
            very_unsatisfied += 1
        else:
            raise Exception("Invalid NPS Score: {}".format(score))
    return [{'y': round((very_satisfied / total) * 100, 0), 'name': 'Very satisfied'},
            {'y': round((satisfied / total) * 100, 0), 'name': 'Satisfied'},
            {'y': round((neutral / total) * 100, 0), 'name': 'Neutral'},
            {'y': round((unsatisfied / total) * 100, 0), 'name': 'Un satisfied'},
            {'y': round((very_unsatisfied / total) * 100, 0), 'name': 'Very unsatisfied'}]


def user_activity_by_apy(activities):
    activities_array = []

    for activity in activities:
        activities_array.append(deepcopy({'y': activity['count'], 'label': activity['value']}))

    return activities_array
