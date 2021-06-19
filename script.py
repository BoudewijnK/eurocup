import json
import os
import requests
import sys

from collections import OrderedDict
from datetime import datetime, timedelta
from dotenv import load_dotenv
from tabulate import tabulate

from eurocup import database

load_dotenv()

EURO_2020_ID = "11997260"
BASE_URL = "https://api.betfair.com/exchange/betting/rest/v1.0/"
HEADERS = {
        'X-Application': os.environ['APP_KEY'],
        'X-Authentication': os.environ['SESSION_TOKEN'],
        'content-type': 'application/json',
}

selection_id_scores = {
    1: (0, 0),
    2: (1, 0),
    3: (1, 1),
    4: (0, 1),
    5: (2, 0),
    6: (2, 1),
    7: (2, 2),
    8: (1, 2),
    9: (0, 2),
    10: (3, 0),
    11: (3, 1),
    12: (3, 2),
    13: (3, 3),
    14: (2, 3),
    15: (1, 3),
    16: (0, 3),
}

scores = list(selection_id_scores.values())


def request_market_ids():
    now = datetime.now()
    future = now + timedelta(days=2)
    data = {
        "filter": {
            "competitionIds": [EURO_2020_ID],
            "marketTypeCodes": ["CORRECT_SCORE"],
            "marketStartTime": {"to": future.strftime('%Y-%m-%dT')},
            "inPlayOnly": False
        },
        "maxResults": 1000,
        "sort": "FIRST_TO_START"
    }
    url = BASE_URL + "listMarketCatalogue/"
    response = requests.post(url=url, data=json.dumps(data), headers=HEADERS)
    if response.status_code != 200:
        exit('Status code != 200')

    market_ids = [result.get('marketId') for result in response.json()]
    return market_ids


def get_market_ids():
    if len(sys.argv) > 1:
        market_ids = sys.argv[1:]
    else:
        market_ids = request_market_ids()
    print(f'{market_ids=}')

    return market_ids


def get_runners(market_id):
    data = f'{{"marketIds": [{market_id}]}}'
    url = BASE_URL + "listMarketBook/"
    response = requests.post(url=url, data=data, headers=HEADERS)
    if response.status_code != 200:
        exit('Status code != 200')
    return response.json()[0]['runners']


def get_event_info(market_id):
    data = {
        "filter": {
            "marketIds": [market_id],
        }
    }
    url = BASE_URL + "listEvents/"
    response = requests.post(url=url, data=json.dumps(data), headers=HEADERS)
    if response.status_code != 200:
        exit('Status code != 200')

    assert len(response.json()) == 1, "We should get exactly one result, provided the market id is valid."

    info = response.json()[0].get('event', {})
    event_name = info.get('name')
    event_time = datetime.strptime(info.get('openDate'), '%Y-%m-%dT%H:%M:%S.%fZ') + timedelta(hours=1)
    print(event_name, '-', event_time.strftime('%a %d %b, %H:%M'))
    database.insert_match(market_id=market_id, event_name=event_name, event_time=event_time)


def calculate_chance(odds):
    return 1 / (odds - 1)


def calculate_probabilities(market_id):
    runners = sorted(get_runners(market_id), key=lambda x: x['selectionId'])
    selection_id_probabilities = dict()
    for runner in runners:
        if (selection_id := runner['selectionId']) in selection_id_scores:
            price = runner.get('lastPriceTraded', 1000)
            chance = calculate_chance(price)
            selection_id_probabilities[selection_id] = chance
    return selection_id_probabilities


def calculate_points(true, prediction):
    """https://www.ekpooltjes.nl/rules/"""

    def winner_correct():
        if true[0] > true[1] and prediction[0] > prediction[1]:
            return True
        elif true[1] > true[0] and prediction[1] > prediction[0]:
            return True
        return False

    def score_partially_correct():
        if true[0] == prediction[0]:
            return True
        elif true[1] == prediction[1]:
            return True
        return False

    if true == prediction:  # COMPLETELY CORRECT
        return 200
    elif true[0] == true[1] and prediction[0] == prediction[1]:  # DRAW CORRECT
        return 100
    elif winner_correct() and score_partially_correct():
        return 95
    elif winner_correct():
        return 75
    elif score_partially_correct():
        return 20
    return 0


def calculate_expected_points(points_per_score, probabilities_of_score):
    return sum([point * prob for point, prob in zip(points_per_score, probabilities_of_score)])


def get_prediction(market_id):
    selection_id_probabilities = calculate_probabilities(market_id)
    expected_points_for_prediction = dict()
    for prediction in scores.copy():
        points_per_score = [calculate_points(real, prediction) for real in scores.copy()]
        expected_points_for_prediction[prediction] = calculate_expected_points(
            points_per_score, list(selection_id_probabilities.values())
        )
    expected_points_for_prediction = OrderedDict(sorted(expected_points_for_prediction.items(),
                                                        key=lambda x: x[1], reverse=True))
    database.insert_predictions(market_id, expected_points_for_prediction)
    print(tabulate(expected_points_for_prediction.items(), headers=["score", "expected poins"], tablefmt="psql"))


def main():
    market_ids = get_market_ids()

    for market_id in market_ids:
        print(f"Match: https://www.betfair.com/exchange/plus/football/market/{market_id}")
        get_event_info(market_id)
        get_prediction(market_id)


if __name__ == '__main__':
    main()
