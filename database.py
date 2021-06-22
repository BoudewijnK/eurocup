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
                   (id integer PRIMARY KEY, market_id text UNIQUE, name text, time text, 
                   goals_a_true integer, goals_b_true integer, goals_a_pred integer, goals_b_pred integer, 
                   points_true integer, points_pred float)''')

    cur.execute(f'''CREATE TABLE IF NOT EXISTS predictions
                    (id integer PRIMARY KEY, 
                    market_id text,
                    time int,
                    {', '.join([f"{score_col} real" for score_col in create_score_cols()])},
                    {', '.join([f"price_{score_col} real" for score_col in create_score_cols()])}
                    )''')

    new_cols = [("goals_a_true", "integer"), ("goals_b_true", "integer"), ("goals_a_pred", "integer"),
                ("goals_b_pred", "integer"), ("points_true", "integer"), ("points_pred", "float")]

    for col_name, col_type in new_cols:
        query = f'''ALTER TABLE matches ADD COLUMN {col_name} {col_type}'''
        print(query)
        cur.execute(query)

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


def insert_predictions(market_id, df):
    score_cols = create_score_cols(df.index.values)
    price_score_cols = [f"price_{c}" for c in score_cols]

    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    query = f'''INSERT INTO predictions (
                        market_id, time, {', '.join(score_cols)}, {', '.join(price_score_cols)}
                    ) VALUES (
                        {market_id}, {int(time())}, {', '.join(map(str, df['expected_points'].values))},
                        {', '.join(map(str, df['price'].values))}
                    )
                    '''
    cur.execute(query)
    con.commit()
    con.close()


if __name__ == '__main__':
    create_tables()
