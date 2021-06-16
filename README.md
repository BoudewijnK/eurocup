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
    
## Example output

```
No input given via command line. Using 182738227.
Match: https://www.betfair.com/exchange/plus/football/market/1.182738227
+---------+------------------+
| score   |   expected poins |
|---------+------------------|
| (1, 1)  |          64.3715 |
| (0, 0)  |          58.8848 |
| (0, 1)  |          54.2425 |
| (1, 0)  |          53.0738 |
| (2, 2)  |          48.3004 |
| (1, 2)  |          46.6827 |
| (2, 1)  |          45.5353 |
| (0, 2)  |          44.1943 |
| (2, 0)  |          42.8191 |
| (3, 3)  |          40.007  |
| (1, 3)  |          38.951  |
| (3, 1)  |          38.2822 |
| (0, 3)  |          37.195  |
| (3, 0)  |          36.5616 |
| (2, 3)  |          33.8423 |
| (3, 2)  |          33.3208 |
+---------+------------------+
```
    
## Resources

- https://docs.developer.betfair.com/visualisers/api-ng-account-operations/