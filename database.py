import sqlite3

from sqlite3 import IntegrityError
from time import time

DB_NAME = "euro2020.db"

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


def create_score_cols(scores=None):
    if scores is None:
        scores = list(selection_id_scores.values())
    return [f"score_{score[0]}_{score[1]}" for score in scores]


def create_tables():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS matches
                   (id integer PRIMARY KEY, market_id text UNIQUE, name text, time text, real_score text)''')

    cur.execute(f'''CREATE TABLE IF NOT EXISTS predictions
                    (id integer PRIMARY KEY, 
                    market_id text,
                    time int,
                    {', '.join([f"{score_col} real" for score_col in create_score_cols()])},
                    {', '.join([f"price_{score_col} real" for score_col in create_score_cols()])}
                    )''')

    # for score_col in create_score_cols():
    #     query = f'''ALTER TABLE predictions ADD COLUMN price_{score_col} real'''
    #     print(query)
    #     cur.execute(query)

    con.commit()
    con.close()


def insert_match(market_id, event_name, event_time):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    query = f'''INSERT INTO matches (
                        market_id, name, time
                    ) VALUES (
                        {market_id}, "{event_name}", "{event_time}"
                    )
                    '''
    try:
        cur.execute(query)
    except IntegrityError:
        print('Integrity error. Most likely market id already exists')
    con.commit()
    con.close()


def insert_predictions(market_id, expected_points_for_prediction, price_of_score):
    score_cols = create_score_cols(expected_points_for_prediction.keys())
    price_score_cols = [f"price_{c}" for c in create_score_cols(price_of_score.keys())]

    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    query = f'''INSERT INTO predictions (
                        market_id, time, {', '.join(score_cols)}, {', '.join(price_score_cols)}
                    ) VALUES (
                        {market_id}, {int(time())}, {', '.join(map(str, expected_points_for_prediction.values()))},
                        {', '.join(map(str, price_of_score.values()))}
                    )
                    '''
    cur.execute(query)
    con.commit()
    con.close()


if __name__ == '__main__':
    create_tables()
