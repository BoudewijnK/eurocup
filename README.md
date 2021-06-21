# Optimize Euro Cup 2020 prediction

I don't watch soccer, but I compete in a Euro Cup 2020 (2021) pool. I use odds from the Betfair exchange to predict the match outcome that is expected to yield the most points.

## Instructions

1. Clone this repo
1. Install requirements
    - `pip install -r requirements.txt`
1. Rename `.env_sample` to `.env` and fill in session token and app key
    - You need a Betfair account but no identification or deposit is required. See here for more detailed instructions: https://developer.betfair.com/en/get-started/#exchange-api
    - Once the session token is expired, you can create a new one here: https://docs.developer.betfair.com/visualisers/api-ng-account-operations/
1. Run the script
    - By default the matches of the next two days are processed
    - You can also submit a market id via the command line
        - `python script.py 1.183116565`
    
## Example output

```
Match: https://www.betfair.com/exchange/plus/football/market/1.183116565
North Macedonia v Netherlands - Mon 21 Jun, 17:00
+--------+---------+---------------+-------------------+
|        |   price |   probability |   expected_points |
|--------+---------+---------------+-------------------|
| (0, 2) |     8.8 |    0.128205   |          64.5971  |
| (0, 3) |     9.6 |    0.116279   |          63.1055  |
| (1, 2) |    11   |    0.1        |          60.5727  |
| (1, 3) |    12   |    0.0909091  |          59.3221  |
| (0, 1) |    13.5 |    0.08       |          58.4933  |
| (2, 3) |    32   |    0.0322581  |          50.62    |
| (1, 1) |    16   |    0.0666667  |          27.454   |
| (0, 0) |    29   |    0.0357143  |          25.1397  |
| (2, 2) |    30   |    0.0344828  |          23.8126  |
| (3, 3) |   130   |    0.00775194 |          20.3419  |
| (1, 0) |    48   |    0.0212766  |          13.4687  |
| (2, 1) |    55   |    0.0185185  |          11.6016  |
| (3, 2) |   120   |    0.00840336 |          11.3593  |
| (3, 1) |   180   |    0.00558659 |           9.11345 |
| (2, 0) |   130   |    0.00775194 |           8.60231 |
| (3, 0) |   550   |    0.00182149 |           6.70927 |
+--------+---------+---------------+-------------------+
```
    
## Resources

- https://developer.betfair.com/en/get-started/#exchange-api
- https://docs.developer.betfair.com/visualisers/api-ng-account-operations/