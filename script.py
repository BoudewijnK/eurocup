import os
import sys
import requests

from tabulate import tabulate
from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) > 1:
    market_id = sys.argv[1]
else:
    market_id = "171635674"  # MANUAL INPUT
    print(f"No input given via command line. Using {market_id}.")
print(f"Match: https://www.betfair.com/exchange/plus/football/market/1.{market_id}")


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


def get_runners():
    base_url = "https://api.betfair.com/exchange/betting/rest/v1.0/"
    data = f'{{"marketIds": [1.{market_id}]}}'
    headers = {
        'X-Application': os.environ['APP_KEY'],
        'X-Authentication': os.environ['SESSION_TOKEN'],
        'content-type': 'application/json',
    }
    url = base_url + "listMarketBook/"
    response = requests.post(url=url, data=data, headers=headers)
    if response.status_code != 200:
        exit('Status code != 200')
    return response.json()[0]['runners']


def calculate_chance(odds):
    return 1 / (odds - 1)


def calculate_probabilities():
    runners = sorted(get_runners(), key=lambda x: x['selectionId'])
    selection_id_probabilities = dict()
    for runner in runners:
        if (selection_id := runner['selectionId']) in selection_id_scores:
            price = runner['lastPriceTraded']
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


def main():
    selection_id_probabilities = calculate_probabilities()
    expected_points_for_prediction = list()
    for prediction in scores.copy():
        points_per_score = [calculate_points(real, prediction) for real in scores.copy()]
        expected_points_for_prediction.append((prediction, calculate_expected_points(
                points_per_score, list(selection_id_probabilities.values())
        )))
    expected_points_for_prediction.sort(key=lambda x: x[1], reverse=True)
    print(tabulate(expected_points_for_prediction, headers=["score", "expected poins"], tablefmt="psql"))


if __name__ == '__main__':
    main()
