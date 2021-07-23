import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

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

scores = list(selection_id_scores.values())


def load_match_df():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    query = "select * from matches "
    cur.execute(query)
    columns = [
        'id',
        'market_id',
        'name',
        'time',
        'real_score',
        'goals_a_true',
        'goals_b_true',
        'goals_a_pred',
        'goals_b_pred',
        'point_true',
        'points_pred',
    ]
    df = pd.DataFrame(cur.fetchall(), columns=columns)
    con.commit()
    con.close()
    return df


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


def verify_df(df):
    """Real scores were manually inserted."""
    cols = [
        'goals_a_true',
        'goals_b_true',
        'goals_a_pred',
        'goals_b_pred',
     ]

    def wrapper(a):
        return calculate_points((a[0], a[1]), (a[2], a[3]))

    df['check'] = df[cols].apply(wrapper, axis=1)
    assert (df["check"] == df["point_true"]).sum() == len(df.index)


def create_score_cols(scores=None):
    if scores is None:
        scores = list(selection_id_scores.values())
    return [f"score_{score[0]}_{score[1]}" for score in scores]


def load_predictions_df():
    columns2 = [
                   'id',
                   'market_id',
                   'time'
               ] + \
               [score_col for score_col in create_score_cols()] + \
               [f"price_{score_col}" for score_col in create_score_cols()]
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    query = "select * from predictions"
    cur.execute(query)
    df2 = pd.DataFrame(cur.fetchall(), columns=columns2)
    con.commit()
    con.close()
    return df2


def modify_df2(df2):
    # only keep the last prediction creation
    df2 = df2.sort_values(by="time", ascending=True)
    df2 = df2.drop_duplicates(subset=['market_id'], keep='last')

    cols = create_score_cols()
    df2['max_expected'] = df2[cols].max(axis=1)

    return df2


def main():
    df = load_match_df()
    df2 = load_predictions_df()
    df2 = modify_df2(df2)

    df = pd.merge(df, df2[['market_id', 'max_expected']], on='market_id', how='left')

    # compare true vs. pred
    df[['true_mean', 'pred_mean']] = df[['point_true', 'max_expected']].expanding().mean()
    plt.figure()
    df[['true_mean', 'pred_mean']].plot()
    plt.savefig('analysis/real_mean_points_vs_expected_mean.png')

    # Few datapoints but it seems like the performance is better for early matches. Maybe structural break from
    # knockout phase. Exchange odds may have been for 90 minutes only whereas scores for the pool were for 90 minutes
    # + extension.
    # Knockout phase started at 26 june. Match id 15 and higher.

    pool_market_ids = [
        '1.182738081',
        '1.182737935',
        '1.183116699',
        '1.183116029',
        '1.183117101',
        '1.183116565',
        '1.183116833',
        '1.183116297',
        '1.18201702',
        '1.183116967',
        '1.183116163',
        '1.182050696',
        '1.183116431',
        '1.182714171',
    ]

    knockout_market_ids = [
        '1.18467344',
        '1.184672162',
        '1.184725734',
        '1.18472662',
        '1.184725882',
        '1.184726472',
        '1.184726768',
        '1.18472697',
        '1.18487912',
        '1.184859432',
        '1.184858205',
        '1.18491261',
        '1.185000698',
        '1.185039907',
        '1.185143755',
    ]

    pool_mask = df['market_id'].isin(pool_market_ids)
    knockout_mask = df['market_id'].isin(knockout_market_ids)

    plt.figure()
    bw = 0.3
    sns.kdeplot(df.loc[pool_mask, 'max_expected'], bw_adjust=bw, label='pool')
    sns.kdeplot(df.loc[knockout_mask, 'max_expected'], bw_adjust=bw, label='knockout')
    plt.legend()
    plt.savefig('analysis/pool_vs_knockout_expected_points.png')

    plt.figure()
    bw = 0.1
    sns.kdeplot(df.loc[pool_mask, 'point_true'], bw_adjust=bw, label='pool')
    sns.kdeplot(df.loc[knockout_mask, 'point_true'], bw_adjust=bw, label='knockout')
    plt.legend()
    plt.savefig('analysis/pool_vs_knockout_true_points.png')

    norm = True
    for mask in [pool_mask, knockout_mask]:
        print(df.loc[mask, 'point_true'].value_counts(normalize=norm))
    #     print(df.loc[mask, 'max_expected'].value_counts(normalize=norm))


if __name__ == '__main__':
    main()
