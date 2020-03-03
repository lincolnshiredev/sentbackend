import pandas as pd
import requests
import json
#https://us-central1-enhanced-bebop-268815.cloudfunctions.net/updateStockPrice?ticker=
def getPrice(ticker: str):
    price = requests.get(url='https://financialmodelingprep.com/api/v3/stock/real-time-price/' + ticker)
    stockPriceDf = pd.DataFrame([pd.read_json(json.dumps(price.json()),typ = 'series')])
    stockPriceDf = stockPriceDf.drop(columns=['symbol'])
   
    return stockPriceDf.to_json()


tickers: str = ['aapl','msft','googl','amzn']
# Example tickers for companies, case insensitive

for ticker in tickers:
    print(getPrice(ticker)) 