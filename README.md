# Optimize EC 2020 prediction

Use Betfair exchange odds to maximize expected points for your match prediction.

## Instructions

1. Request api key at Betfair. 
    - see: https://developer.betfair.com/en/get-started/#exchange-api
1. Rename `.env_sample` to `.env` and enter obtained session and api key
1. Search for upcoming match and copy the match id
    - e.g. France vs. Germany has match id `171635674`. See https://www.betfair.com/exchange/plus/football/market/1.171635674
1. Run script
    - e.g. `python script.py 171635674`  